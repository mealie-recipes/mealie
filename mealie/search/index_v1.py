"""Version 1 search schema. Preserve this module for historical migrations."""

import json
import sqlite3

import sqlalchemy as sa
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.event import listens_for

from .normalization_v1 import COMBINING_MARKS, LIGATURES, normalize

segments = sa.table(
    "recipe_search_segments",
    sa.column("key", sa.String),
    sa.column("recipe_id", sa.String),
    sa.column("field", sa.Integer),
    sa.column("content", sa.String),
)
terms = sa.table(
    "recipe_search_terms",
    sa.column("recipe_id", sa.String),
    sa.column("term", sa.String),
    sa.column("length", sa.Integer),
)


def register_sqlite(connection: sqlite3.Connection) -> None:
    connection.create_function("recipe_search_normalize", 1, lambda value: normalize(value or ""), deterministic=True)
    connection.create_function(
        "recipe_search_words", 1, lambda value: json.dumps(sorted(set((value or "").split()))), deterministic=True
    )


@listens_for(Engine, "connect")
def register_search_functions(dbapi_connection: object, connection_record: object) -> None:
    if isinstance(dbapi_connection, sqlite3.Connection):
        register_sqlite(dbapi_connection)


def _source_select() -> str:
    return """
        SELECT 'title:' || CAST(id AS TEXT) AS key, CAST(id AS TEXT) AS recipe_id, 0 AS field,
               recipe_search_normalize(name) AS content FROM recipes
        UNION ALL
        SELECT 'description:' || CAST(id AS TEXT), CAST(id AS TEXT), 1,
               recipe_search_normalize(description) FROM recipes
        UNION ALL
        SELECT 'note:' || CAST(id AS TEXT), CAST(recipe_id AS TEXT), 2,
               recipe_search_normalize(note) FROM recipes_ingredients
        UNION ALL
        SELECT 'original:' || CAST(id AS TEXT), CAST(recipe_id AS TEXT), 2,
               recipe_search_normalize(original_text) FROM recipes_ingredients
        UNION ALL
        SELECT 'food:' || CAST(i.id AS TEXT), CAST(i.recipe_id AS TEXT), 2,
               recipe_search_normalize(f.name) FROM recipes_ingredients i
               JOIN ingredient_foods f ON f.id = i.food_id
    """


def rebuild(connection: Connection) -> None:
    """Rebuild projections inside the caller's transaction."""
    # Serialize with source writes on PostgreSQL so a rebuild cannot lose concurrent edits.
    if connection.dialect.name == "postgresql":
        connection.exec_driver_sql(
            "LOCK TABLE recipes, recipes_ingredients, ingredient_foods IN SHARE ROW EXCLUSIVE MODE"
        )
    connection.exec_driver_sql("DELETE FROM recipe_search_segments")
    connection.exec_driver_sql(
        "INSERT INTO recipe_search_segments (key, recipe_id, field, content) " + _source_select()
    )


def install(connection: Connection) -> None:
    sqlite = connection.dialect.name == "sqlite"
    if sqlite:
        register_sqlite(connection.connection.driver_connection)
    else:
        normalized = f"lower(translate(normalize(coalesce(value, ''), NFKD), '{COMBINING_MARKS}', ''))"
        for source, replacement in LIGATURES.items():
            normalized = f"replace({normalized}, '{source}', '{replacement}')"
        connection.exec_driver_sql(f"""
            CREATE FUNCTION recipe_search_normalize(value TEXT) RETURNS TEXT LANGUAGE SQL STABLE AS $$
                SELECT trim(regexp_replace({normalized}, '[^[:alnum:]]+', ' ', 'g'))
            $$
        """)
    connection.exec_driver_sql("""
        CREATE TABLE recipe_search_segments (
            key TEXT PRIMARY KEY, recipe_id TEXT NOT NULL, field INTEGER NOT NULL, content TEXT NOT NULL
        )
    """)
    connection.exec_driver_sql(
        "CREATE INDEX ix_recipe_search_segments_recipe ON recipe_search_segments(recipe_id, field)"
    )
    connection.exec_driver_sql("""
        CREATE TABLE recipe_search_terms (
            recipe_id TEXT NOT NULL, term TEXT NOT NULL, length INTEGER NOT NULL,
            PRIMARY KEY(recipe_id, term)
        )
    """)
    connection.exec_driver_sql("CREATE INDEX ix_recipe_search_terms_length ON recipe_search_terms(length, term)")
    if sqlite:
        connection.exec_driver_sql("""
            CREATE VIRTUAL TABLE recipe_search_fts USING fts5(
                content, content='recipe_search_segments', content_rowid='rowid', tokenize='ascii', prefix='2 3 4'
            )
        """)
        for action, body in {
            "insert": "INSERT INTO recipe_search_fts(rowid, content) VALUES (new.rowid, new.content);",
            "delete": """INSERT INTO recipe_search_fts(recipe_search_fts,rowid,content)
                         VALUES('delete',old.rowid,old.content);""",
            "update": """INSERT INTO recipe_search_fts(recipe_search_fts,rowid,content)
                        VALUES('delete',old.rowid,old.content);
                        INSERT INTO recipe_search_fts(rowid,content) VALUES(new.rowid,new.content);""",
        }.items():
            connection.exec_driver_sql(
                f"CREATE TRIGGER recipe_search_fts_{action} AFTER {action} ON recipe_search_segments BEGIN {body} END"
            )
        for action in ("insert", "update", "delete"):
            record = "old" if action == "delete" else "new"
            add = (
                ""
                if action == "delete"
                else """
                INSERT OR IGNORE INTO recipe_search_terms(recipe_id,term,length)
                SELECT new.recipe_id,value,length(value) FROM json_each(recipe_search_words(new.content));
            """
            )
            connection.exec_driver_sql(f"""
                CREATE TRIGGER recipe_search_terms_{action} AFTER {action} ON recipe_search_segments
                WHEN {record}.field=0 BEGIN
                    DELETE FROM recipe_search_terms WHERE recipe_id={record}.recipe_id;
                    {add}
                END
            """)
        _sqlite_source_triggers(connection)
    else:
        connection.exec_driver_sql("""
            ALTER TABLE recipe_search_segments ADD COLUMN document tsvector
                GENERATED ALWAYS AS (to_tsvector('simple'::regconfig, content)) STORED
        """)
        connection.exec_driver_sql(
            "CREATE INDEX ix_recipe_search_document ON recipe_search_segments USING gin(document)"
        )
        connection.exec_driver_sql("""
            CREATE FUNCTION recipe_search_update_terms() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
                IF TG_OP <> 'INSERT' AND OLD.field=0 THEN
                    DELETE FROM recipe_search_terms WHERE recipe_id=OLD.recipe_id;
                END IF;
                IF TG_OP <> 'DELETE' AND NEW.field=0 THEN
                    INSERT INTO recipe_search_terms(recipe_id,term,length)
                    SELECT NEW.recipe_id,word,length(word)
                    FROM (SELECT DISTINCT unnest(string_to_array(NEW.content,' ')) AS word) words
                    WHERE word <> '' ON CONFLICT DO NOTHING;
                END IF;
                RETURN NULL;
            END $$
        """)
        connection.exec_driver_sql("""
            CREATE TRIGGER recipe_search_terms_change AFTER INSERT OR UPDATE OR DELETE ON recipe_search_segments
            FOR EACH ROW EXECUTE FUNCTION recipe_search_update_terms()
        """)
        _postgres_source_triggers(connection)
    rebuild(connection)


def _sqlite_source_triggers(connection: Connection) -> None:
    for table, prefix, insert in _source_trigger_specs():
        for action in ("insert", "update", "delete"):
            reference = "old" if action == "delete" else "new"
            delete = f"DELETE FROM recipe_search_segments WHERE {prefix.format(record=reference)};"
            if action == "update":
                delete = f"DELETE FROM recipe_search_segments WHERE {prefix.format(record='old')};"
            if table == "recipes" and action != "delete":
                delete = (
                    "DELETE FROM recipe_search_segments WHERE key IN "
                    f"('title:'||CAST({reference}.id AS TEXT),'description:'||CAST({reference}.id AS TEXT));"
                )
            body = delete + ("" if action == "delete" else insert)
            event = "UPDATE OF name, description" if table == "recipes" and action == "update" else action
            connection.exec_driver_sql(
                f"CREATE TRIGGER recipe_search_{table}_{action} AFTER {event} ON {table} BEGIN {body} END"
            )


def _source_trigger_specs() -> list[tuple[str, str, str]]:
    return [
        (
            "recipes",
            "recipe_id=CAST({record}.id AS TEXT)",
            """INSERT INTO recipe_search_segments(key,recipe_id,field,content) VALUES
                ('title:'||CAST(new.id AS TEXT),CAST(new.id AS TEXT),0,recipe_search_normalize(new.name)),
                ('description:'||CAST(new.id AS TEXT),CAST(new.id AS TEXT),1,
                 recipe_search_normalize(new.description));""",
        ),
        (
            "recipes_ingredients",
            "key IN ('note:'||CAST({record}.id AS TEXT),"
            "'original:'||CAST({record}.id AS TEXT),'food:'||CAST({record}.id AS TEXT))",
            """INSERT INTO recipe_search_segments(key,recipe_id,field,content) VALUES
                ('note:'||CAST(new.id AS TEXT),CAST(new.recipe_id AS TEXT),2,recipe_search_normalize(new.note)),
                ('original:'||CAST(new.id AS TEXT),CAST(new.recipe_id AS TEXT),2,
                 recipe_search_normalize(new.original_text));
                INSERT INTO recipe_search_segments(key,recipe_id,field,content)
                SELECT 'food:'||CAST(new.id AS TEXT),CAST(new.recipe_id AS TEXT),2,recipe_search_normalize(name)
                FROM ingredient_foods WHERE id=new.food_id;""",
        ),
        (
            "ingredient_foods",
            "key IN (SELECT 'food:'||CAST(id AS TEXT) FROM recipes_ingredients WHERE food_id={record}.id)",
            """INSERT INTO recipe_search_segments(key,recipe_id,field,content)
                SELECT 'food:'||CAST(id AS TEXT),CAST(recipe_id AS TEXT),2,recipe_search_normalize(new.name)
                FROM recipes_ingredients WHERE food_id=new.id;""",
        ),
    ]


def _postgres_source_triggers(connection: Connection) -> None:
    for table, prefix, insert in _source_trigger_specs():
        delete = f"DELETE FROM recipe_search_segments WHERE {prefix.format(record='old')};"
        if table == "recipes":
            delete = """
                IF TG_OP='DELETE' THEN
                    DELETE FROM recipe_search_segments WHERE recipe_id=CAST(old.id AS TEXT);
                ELSE
                    DELETE FROM recipe_search_segments WHERE key IN
                        ('title:'||CAST(old.id AS TEXT),'description:'||CAST(old.id AS TEXT));
                END IF;
            """
        connection.exec_driver_sql(f"""
            CREATE FUNCTION recipe_search_{table}_change() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
                IF TG_OP <> 'INSERT' THEN
                    {delete}
                END IF;
                IF TG_OP <> 'DELETE' THEN
                    {insert}
                END IF;
                RETURN NULL;
            END $$
        """)
        connection.exec_driver_sql(f"""
            CREATE TRIGGER recipe_search_{table}_change AFTER INSERT OR UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION recipe_search_{table}_change()
        """)


def uninstall(connection: Connection) -> None:
    sqlite = connection.dialect.name == "sqlite"
    for table, _, _ in _source_trigger_specs():
        if sqlite:
            for action in ("insert", "update", "delete"):
                connection.exec_driver_sql(f"DROP TRIGGER recipe_search_{table}_{action}")
        else:
            connection.exec_driver_sql(f"DROP TRIGGER recipe_search_{table}_change ON {table}")
            connection.exec_driver_sql(f"DROP FUNCTION recipe_search_{table}_change()")
    if sqlite:
        connection.exec_driver_sql("DROP TABLE recipe_search_fts")
    connection.exec_driver_sql("DROP TABLE recipe_search_segments")
    connection.exec_driver_sql("DROP TABLE recipe_search_terms")
    if not sqlite:
        connection.exec_driver_sql("DROP FUNCTION recipe_search_update_terms()")
        connection.exec_driver_sql("DROP FUNCTION recipe_search_normalize(TEXT)")
