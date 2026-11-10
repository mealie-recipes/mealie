import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file

LEGACY_JOIN_TABLES = {
    "cookbooks_to_categories": ("cookbook_id", "category_id"),
    "cookbooks_to_tags": ("cookbook_id", "tag_id"),
    "cookbooks_to_tools": ("cookbook_id", "tool_id"),
    "plan_rules_to_categories": ("group_plan_rule_id", "category_id"),
    "plan_rules_to_tags": ("plan_rule_id", "tag_id"),
}

# join tables the migration has no business touching
UNRELATED_JOIN_TABLES = {
    "plan_rules_to_households": ("group_plan_rule_id", "household_id"),
    "recipes_to_categories": ("recipe_id", "category_id"),
}


def _migration():
    path = next(ALEMBIC_MIGRATIONS.glob("*3697d65c5f92*.py"))
    return import_file("clear_legacy_organizer_join_tables", path)


def _count(connection: sa.Connection, table: str) -> int:
    return connection.execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar_one()


def test_clear_legacy_organizer_join_tables_empties_only_legacy_tables() -> None:
    migration = _migration()
    engine = sa.create_engine("sqlite://")

    try:
        with engine.connect() as connection:
            for table, (left, right) in (LEGACY_JOIN_TABLES | UNRELATED_JOIN_TABLES).items():
                connection.execute(sa.text(f"CREATE TABLE {table} ({left} CHAR(32), {right} CHAR(32))"))
                connection.execute(
                    sa.text(f"INSERT INTO {table} ({left}, {right}) VALUES ('a', 'b'), ('a', 'c'), ('d', 'b')")
                )

            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()

            inspector = sa.inspect(connection)
            for table in LEGACY_JOIN_TABLES:
                assert inspector.has_table(table), f"{table} should be kept"
                assert _count(connection, table) == 0, f"{table} should be empty"

            for table in UNRELATED_JOIN_TABLES:
                assert _count(connection, table) == 3, f"{table} should be untouched"

            with Operations.context(MigrationContext.configure(connection)):
                migration.downgrade()

            for table in LEGACY_JOIN_TABLES:
                assert _count(connection, table) == 0
    finally:
        engine.dispose()
