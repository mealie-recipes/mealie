import datetime
import json
from pathlib import Path

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import base
from sqlalchemy.orm import Session, sessionmaker

from mealie.services._base_service import BaseService


class AlchemyExporter(BaseService):
    connection_str: str
    engine: base.Engine
    meta: MetaData

    look_for_datetime = {"created_at", "update_at", "date_updated", "timestamp", "expires_at"}
    look_for_date = {"date_added", "date"}

    class DateTimeParser(BaseModel):
        date: datetime.date = None
        time: datetime.datetime = None

    def __init__(self, connection_str: str) -> None:
        super().__init__()

        self.connection_str = connection_str
        self.engine = create_engine(connection_str)
        self.meta = MetaData()
        self.session_maker = sessionmaker(bind=self.engine)

    @staticmethod
    def convert_to_datetime(data: dict) -> dict:
        """
        walks the dictionary to convert all things that look like timestamps to datetime objects
        used in the context of reading a json file into a database via SQLAlchemy.
        """
        for key, value in data.items():
            if isinstance(value, dict):
                data = AlchemyExporter.convert_to_datetime(value)
            elif isinstance(value, list):  # assume that this is a list of dictionaries
                data[key] = [AlchemyExporter.convert_to_datetime(item) for item in value]
            elif isinstance(value, str):
                if key in AlchemyExporter.look_for_datetime:
                    data[key] = AlchemyExporter.DateTimeParser(time=value).time
                if key in AlchemyExporter.look_for_date:
                    data[key] = AlchemyExporter.DateTimeParser(date=value).date

        return data

    @staticmethod
    def _compare_schemas(schema1: dict, schema2: dict) -> bool:
        try:
            # validate alembic version(s) are the same
            return schema1["alembic_version"] == schema2["alembic_version"]
        except KeyError:
            return False

    @staticmethod
    def validate_schemas(schema1: Path | dict, schema2: Path | dict) -> bool:
        """
        Validates that the schema of the database matches the schema of the database. In practice,
        this means validating that the alembic version is the same
        """

        def extract_json(file: Path) -> dict:
            with open(file) as f:
                return json.loads(f.read())

        if isinstance(schema1, Path):
            schema1 = extract_json(schema1)

        if isinstance(schema2, Path):
            schema2 = extract_json(schema2)

        return AlchemyExporter._compare_schemas(schema1, schema2)

    def dump_schema(self) -> dict:
        """
        Returns the schema of the SQLAlchemy database as a python dictionary. This dictionary is wrapped by
        jsonable_encoder to ensure that the object can be converted to a json string.
        """
        self.meta.reflect(bind=self.engine)

        all_tables = self.meta.tables.values()

        results = {
            **{table.name: [] for table in all_tables},
            "alembic_version": [dict(row) for row in self.engine.execute("SELECT * FROM alembic_version").fetchall()],
        }

        return jsonable_encoder(results)

    def dump(self) -> dict:
        """
        Returns the entire SQLAlchemy database as a python dictionary. This dictionary is wrapped by
        jsonable_encoder to ensure that the object can be converted to a json string.
        """
        self.meta.reflect(bind=self.engine)  # http://docs.sqlalchemy.org/en/rel_0_9/core/reflection.html
        result = {
            table.name: [dict(row) for row in self.engine.execute(table.select())] for table in self.meta.sorted_tables
        }

        return jsonable_encoder(result)

    def restore(self, db_dump: dict) -> None:
        """Restores all data from dictionary into the database"""
        data = AlchemyExporter.convert_to_datetime(db_dump)

        self.meta.reflect(bind=self.engine)

        with self.session_maker() as session:
            for table_name, rows in data.items():
                if not rows:
                    continue

                table = self.meta.tables[table_name]
                session.execute(table.insert(), rows)

            session.commit()

    def drop_all(self) -> None:
        """Drops all data from the database"""
        self.meta.reflect(bind=self.engine)

        with self.session_maker() as session:
            session: Session

            for table in self.meta.sorted_tables:
                session.execute(f"DELETE FROM {table.name}")

            session.commit()
