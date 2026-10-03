import json
from datetime import UTC, datetime

import pytest
from sqlalchemy import JSON, Column, DateTime, Integer, MetaData, Table, insert, select

from mealie.core.config import get_app_settings
from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.datetime import NaiveDateTime
from mealie.services.backups_v2.alchemy_exporter import AlchemyExporter
from tests.utils.alembic_reader import alembic_versions


def test_alchemy_exporter():
    settings = get_app_settings()
    exporter = AlchemyExporter(settings.DB_URL)
    data = exporter.dump()

    assert data["alembic_version"] == alembic_versions()
    assert json.dumps(data, indent=4)  # Make sure data is json-serializable

    exporter.engine.dispose()


def test_every_datetime_column_survives_a_backup():
    """Restores rebuild datetimes by column name, so an unregistered one comes back as a string.

    The failure is silent at backup time and only shows up on restore, so this asserts the two stay
    in step rather than waiting for someone to notice a broken restore.
    """
    datetime_columns = {
        column.name
        for table in SqlAlchemyBase.metadata.tables.values()
        for column in table.columns
        if isinstance(column.type, NaiveDateTime)
    }

    unregistered = datetime_columns - AlchemyExporter.look_for_datetime
    assert not unregistered, (
        f"datetime columns missing from AlchemyExporter.look_for_datetime: {sorted(unregistered)}. "
        "Add them, or they will restore as strings."
    )


@pytest.mark.parametrize("table_name", ["recipes_ingredients", "shopping_list_items"])
@pytest.mark.parametrize(
    "snapshot",
    [
        None,
        {
            "source_id": "c5866fe8-6d61-4e25-9f07-dc10dad33bdf",
            "name": "tomato",
            "extras": {
                "origin": "garden",
                "created_at": "not a database timestamp",
                "date": "2026-09-24",
                "nested": {"id": "c5866fe8-6d61-4e25-9f07-dc10dad33bdf"},
                "values": ["text", 3, True, None, {"date": "unchanged"}],
            },
        },
    ],
)
def test_json_snapshot_survives_backup_conversion(table_name: str, snapshot: dict | None):
    exporter = AlchemyExporter("sqlite://")
    metadata = MetaData()
    table = Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("created_at", DateTime),
        Column("food_snapshot", JSON(none_as_null=True)),
    )
    try:
        metadata.create_all(exporter.engine)
        exporter.meta.reflect(bind=exporter.engine)
        original = {
            "id": 1,
            "created_at": datetime(2026, 9, 24, tzinfo=UTC).replace(tzinfo=None),
            "food_snapshot": snapshot,
        }
        with exporter.engine.begin() as connection:
            connection.execute(insert(table), original)
            rows = [dict(row) for row in connection.execute(select(table)).mappings()]
        # Simulate the JSON file written by a backup, then restore into the reflected table.
        backup = json.loads(json.dumps({table_name: rows}, default=str))
        converted = exporter.convert_types(backup)
        assert converted[table_name][0] == original
        with exporter.engine.begin() as connection:
            connection.execute(table.delete())
            connection.execute(insert(exporter.meta.tables[table_name]), converted[table_name])
            restored = dict(connection.execute(select(table)).mappings().one())
        assert restored == original
    finally:
        exporter.engine.dispose()
