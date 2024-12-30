import datetime
import os
import uuid
from logging import Logger
from os import path
from textwrap import dedent
from typing import Any

from alembic import command
from alembic.config import Config
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import Connection, ForeignKey, ForeignKeyConstraint, MetaData, Table, create_engine, insert, text
from sqlalchemy.engine import base
from sqlalchemy.orm import sessionmaker

from mealie.db import init_db
from mealie.db.fixes.fix_migration_data import fix_migration_data
from mealie.db.init_db import ALEMBIC_DIR
from mealie.db.models._model_utils.guid import GUID
from mealie.services._base_service import BaseService


class ForeignKeyDisabler:
    def __init__(self, connection: Connection, dialect_name: str, *, logger: Logger | None = None):
        self.connection = connection
        self.is_postgres = dialect_name == "postgresql"
        self.logger = logger

        self._initial_fk_state: str | None = None

    def __enter__(self):
        if self.is_postgres:
            self._initial_fk_state = self.connection.execute(text("SHOW session_replication_role;")).scalar()
            self.connection.execute(text("SET session_replication_role = 'replica';"))
        else:
            self._initial_fk_state = self.connection.execute(text("PRAGMA foreign_keys;")).scalar()
            self.connection.execute(text("PRAGMA foreign_keys = OFF;"))

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.is_postgres:
                initial_state = self._initial_fk_state or "origin"
                self.connection.execute(text(f"SET session_replication_role = '{initial_state}';"))
            else:
                initial_state = self._initial_fk_state or "ON"
                self.connection.execute(text(f"PRAGMA foreign_keys = {initial_state};"))
        except Exception:
            if self.logger:
                self.logger.exception("Error when re-enabling foreign keys")
            raise


class AlchemyExporter(BaseService):
    connection_str: str
    engine: base.Engine
    meta: MetaData

    look_for_datetime = {"created_at", "update_at", "date_updated", "timestamp", "expires_at", "locked_at", "last_made"}
    look_for_date = {"date_added", "date"}
    look_for_time = {"scheduled_time"}

    class DateTimeParser(BaseModel):
        date: datetime.date | None = None
        dt: datetime.datetime | None = None
        time: datetime.time | None = None

    def __init__(self, connection_str: str) -> None:
        super().__init__()

        self.connection_str = connection_str
        self.engine = create_engine(connection_str)
        self.meta = MetaData()
        self.session_maker = sessionmaker(bind=self.engine)

    @staticmethod
    def is_uuid(value: Any) -> bool:
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_foreign_key(db_dump: dict[str, list[dict]], fk: ForeignKey, fk_value: Any) -> bool:
        if not fk_value:
            return True

        foreign_table_name = fk.column.table.name
        foreign_field_name = fk.column.name

        for row in db_dump.get(foreign_table_name, []):
            if row[foreign_field_name] == fk_value:
                return True

        return False

    def convert_types(self, data: dict) -> dict:
        """
        walks the dictionary to restore all things that look like string representations of their complex types
        used in the context of reading a json file into a database via SQLAlchemy.
        """
        for key, value in data.items():
            if isinstance(value, dict):
                data = self.convert_types(value)
            elif isinstance(value, list):  # assume that this is a list of dictionaries
                data[key] = [self.convert_types(item) for item in value]
            elif isinstance(value, str):
                if self.is_uuid(value):
                    # convert the data to the current database's native GUID type
                    data[key] = GUID.convert_value_to_guid(value, self.engine.dialect)
                if key in self.look_for_datetime:
                    data[key] = self.DateTimeParser(dt=value).dt
                if key in self.look_for_date:
                    data[key] = self.DateTimeParser(date=value).date
                if key in self.look_for_time:
                    data[key] = self.DateTimeParser(time=value).time
        return data

    def clean_rows(self, db_dump: dict[str, list[dict]], table: Table, rows: list[dict]) -> list[dict]:
        """
        Checks rows against foreign key restraints and removes any rows that would violate them
        """

        fks = table.foreign_keys

        valid_rows = []
        for row in rows:
            is_valid_row = True
            for fk in fks:
                fk_value = row.get(fk.parent.name)
                if self.is_valid_foreign_key(db_dump, fk, row.get(fk.parent.name)):
                    continue

                is_valid_row = False
                self.logger.warning(
                    f"Removing row from table {table.name} because of invalid foreign key {fk.parent.name}: {fk_value}"
                )
                self.logger.warning(f"Row: {row}")
                break

            if is_valid_row:
                valid_rows.append(row)

        return valid_rows

    def dump_schema(self) -> dict:
        """
        Returns the schema of the SQLAlchemy database as a python dictionary. This dictionary is wrapped by
        jsonable_encoder to ensure that the object can be converted to a json string.
        """
        with self.engine.connect() as connection:
            self.meta.reflect(bind=self.engine)

            all_tables = self.meta.tables.values()

            results = {
                **{table.name: [] for table in all_tables},
                "alembic_version": [
                    dict(row) for row in connection.execute(text("SELECT * FROM alembic_version")).mappings()
                ],
            }

            return jsonable_encoder(results)

    def dump(self) -> dict[str, list[dict]]:
        """
        Returns the entire SQLAlchemy database as a python dictionary. This dictionary is wrapped by
        jsonable_encoder to ensure that the object can be converted to a json string.
        """

        # run database fixes first so we aren't backing up bad data
        with self.session_maker() as session:
            try:
                fix_migration_data(session)
            except Exception:
                self.logger.error("Error fixing migration data during export; continuing anyway")

        with self.engine.connect() as connection:
            self.meta.reflect(bind=self.engine)  #  http://docs.sqlalchemy.org/en/rel_0_9/core/reflection.html

            result = {
                table.name: [dict(row) for row in connection.execute(table.select()).mappings()]
                for table in self.meta.sorted_tables
            }

        return jsonable_encoder(result)

    def restore(self, db_dump: dict) -> None:
        # setup alembic to run migrations up the version of the backup
        alembic_data = db_dump["alembic_version"]
        alembic_version = alembic_data[0]["version_num"]

        alembic_cfg_path = os.getenv("ALEMBIC_CONFIG_FILE", default=str(ALEMBIC_DIR / "alembic.ini"))

        if not path.isfile(alembic_cfg_path):
            raise Exception("Provided alembic config path doesn't exist")

        alembic_cfg = Config(alembic_cfg_path)
        command.upgrade(alembic_cfg, alembic_version)

        del db_dump["alembic_version"]
        """Restores all data from dictionary into the database"""
        with self.engine.begin() as connection:
            with ForeignKeyDisabler(connection, self.engine.dialect.name, logger=self.logger):
                data = self.convert_types(db_dump)

                self.meta.reflect(bind=self.engine)
                for table_name, rows in data.items():
                    if not rows:
                        continue
                    table = self.meta.tables[table_name]
                    rows = self.clean_rows(db_dump, table, rows)

                    connection.execute(table.delete())
                    connection.execute(insert(table), rows)
                if self.engine.dialect.name == "postgresql":
                    # Restore postgres sequence numbers
                    sequences = [
                        ("api_extras_id_seq", "api_extras"),
                        ("group_meal_plans_id_seq", "group_meal_plans"),
                        ("ingredient_food_extras_id_seq", "ingredient_food_extras"),
                        ("invite_tokens_id_seq", "invite_tokens"),
                        ("long_live_tokens_id_seq", "long_live_tokens"),
                        ("notes_id_seq", "notes"),
                        ("password_reset_tokens_id_seq", "password_reset_tokens"),
                        ("recipe_assets_id_seq", "recipe_assets"),
                        ("recipe_ingredient_ref_link_id_seq", "recipe_ingredient_ref_link"),
                        ("recipe_nutrition_id_seq", "recipe_nutrition"),
                        ("recipe_settings_id_seq", "recipe_settings"),
                        ("recipes_ingredients_id_seq", "recipes_ingredients"),
                        ("server_tasks_id_seq", "server_tasks"),
                        ("shopping_list_extras_id_seq", "shopping_list_extras"),
                        ("shopping_list_item_extras_id_seq", "shopping_list_item_extras"),
                    ]

                    sql = "\n".join(
                        [f"SELECT SETVAL('{seq}', (SELECT MAX(id) FROM {table}));" for seq, table in sequences]
                    )
                    connection.execute(text(dedent(sql)))

        # Re-init database to finish migrations
        init_db.main()

    def drop_all(self) -> None:
        """Drops all data from the database"""
        from sqlalchemy.engine.reflection import Inspector
        from sqlalchemy.schema import DropConstraint, DropTable, MetaData, Table

        with self.engine.begin() as connection:
            inspector = Inspector.from_engine(self.engine)

            # We need to re-create a minimal metadata with only the required things to
            # successfully emit drop constraints and tables commands for postgres (based
            # on the actual schema of the running instance)
            meta = MetaData()
            tables = []
            all_fkeys = []
            for table_name in inspector.get_table_names():
                fkeys = []

                for fkey in inspector.get_foreign_keys(table_name):
                    if not fkey["name"]:
                        continue

                    fkeys.append(ForeignKeyConstraint((), (), name=fkey["name"]))

                tables.append(Table(table_name, meta, *fkeys))
                all_fkeys.extend(fkeys)

            if self.engine.dialect.name == "postgresql":
                # Only pg needs foreign key dropping
                for fkey in all_fkeys:
                    connection.execute(DropConstraint(fkey))

                for table in tables:
                    connection.execute(DropTable(table))
                # I have no idea how to drop all custom types with sqlalchemy
                # Since we only have one, this will have to do for now
                connection.execute(text("DROP TYPE authmethod"))
            else:
                for table in tables:
                    connection.execute(DropTable(table))
