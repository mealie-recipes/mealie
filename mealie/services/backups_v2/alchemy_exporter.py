import datetime
import uuid
from os import path
from pathlib import Path

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import ForeignKeyConstraint, MetaData, create_engine, insert, text
from sqlalchemy.engine import base
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config
from mealie.db import init_db
from mealie.db.models._model_utils import GUID
from mealie.services._base_service import BaseService

PROJECT_DIR = Path(__file__).parent.parent.parent.parent


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
    def is_uuid(value: str) -> bool:
        try:
            uuid.UUID(value)
            return True
        except ValueError:
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

        alembic_cfg = Config(str(PROJECT_DIR / "alembic.ini"))
        # alembic's file resolver wants to use the "mealie" subdirectory when called from within the server package
        # Just override this to use the correct migrations path
        alembic_cfg.set_main_option("script_location", path.join(PROJECT_DIR, "alembic"))
        command.upgrade(alembic_cfg, alembic_version)

        del db_dump["alembic_version"]
        """Restores all data from dictionary into the database"""
        with self.engine.begin() as connection:
            data = self.convert_types(db_dump)

            self.meta.reflect(bind=self.engine)
            for table_name, rows in data.items():
                if not rows:
                    continue
                table = self.meta.tables[table_name]

                connection.execute(table.delete())
                connection.execute(insert(table), rows)
            if self.engine.dialect.name == "postgresql":
                # Restore postgres sequence numbers
                connection.execute(
                    text(
                        """
                SELECT SETVAL('api_extras_id_seq', (SELECT MAX(id) FROM api_extras));
SELECT SETVAL('group_meal_plans_id_seq', (SELECT MAX(id) FROM group_meal_plans));
SELECT SETVAL('ingredient_food_extras_id_seq', (SELECT MAX(id) FROM ingredient_food_extras));
SELECT SETVAL('invite_tokens_id_seq', (SELECT MAX(id) FROM invite_tokens));
SELECT SETVAL('long_live_tokens_id_seq', (SELECT MAX(id) FROM long_live_tokens));
SELECT SETVAL('notes_id_seq', (SELECT MAX(id) FROM notes));
SELECT SETVAL('password_reset_tokens_id_seq', (SELECT MAX(id) FROM password_reset_tokens));
SELECT SETVAL('recipe_assets_id_seq', (SELECT MAX(id) FROM recipe_assets));
SELECT SETVAL('recipe_ingredient_ref_link_id_seq', (SELECT MAX(id) FROM recipe_ingredient_ref_link));
SELECT SETVAL('recipe_nutrition_id_seq', (SELECT MAX(id) FROM recipe_nutrition));
SELECT SETVAL('recipe_settings_id_seq', (SELECT MAX(id) FROM recipe_settings));
SELECT SETVAL('recipes_ingredients_id_seq', (SELECT MAX(id) FROM recipes_ingredients));
SELECT SETVAL('server_tasks_id_seq', (SELECT MAX(id) FROM server_tasks));
SELECT SETVAL('shopping_list_extras_id_seq', (SELECT MAX(id) FROM shopping_list_extras));
SELECT SETVAL('shopping_list_item_extras_id_seq', (SELECT MAX(id) FROM shopping_list_item_extras));
"""
                    )
                )

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
