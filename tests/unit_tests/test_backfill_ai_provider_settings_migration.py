import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file


def _migration():
    path = next(ALEMBIC_MIGRATIONS.glob("*071e03b4f851*.py"))
    return import_file("backfill_missing_ai_provider_settings", path)


def test_migration_backfills_only_missing_settings() -> None:
    engine = sa.create_engine("sqlite://")
    try:
        with engine.connect() as connection:
            connection.execute(sa.text("CREATE TABLE groups (id CHAR(32) PRIMARY KEY)"))
            connection.execute(
                sa.text("CREATE TABLE ai_provider_settings (id CHAR(32) PRIMARY KEY, group_id CHAR(32) UNIQUE)")
            )
            connection.execute(sa.text("INSERT INTO groups (id) VALUES (:a), (:b)"), {"a": "a" * 32, "b": "b" * 32})
            connection.execute(
                sa.text("INSERT INTO ai_provider_settings (id, group_id) VALUES (:id, :group_id)"),
                {"id": "c" * 32, "group_id": "a" * 32},
            )

            with Operations.context(MigrationContext.configure(connection)):
                _migration().upgrade()

            rows = list(connection.execute(sa.text("SELECT id, group_id FROM ai_provider_settings")))
    finally:
        engine.dispose()

    assert sorted(row.group_id for row in rows) == ["a" * 32, "b" * 32]
    assert ("c" * 32, "a" * 32) in [tuple(row) for row in rows]
