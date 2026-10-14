from io import StringIO
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file

migration = import_file("recipe_migration_identity", next(ALEMBIC_MIGRATIONS.glob("*e4b68c9a105d*.py")))


def test_identity_schema_upgrade_downgrade(tmp_path: Path) -> None:
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'migration.db'}")
    try:
        with engine.begin() as connection:
            connection.execute(sa.text("CREATE TABLE households (id CHAR(32) PRIMARY KEY)"))
            connection.execute(sa.text("CREATE TABLE recipes (id CHAR(32) PRIMARY KEY)"))
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()
                assert "recipe_migrations" in sa.inspect(connection).get_table_names()
                constraints = sa.inspect(connection).get_unique_constraints("recipe_migrations")
                assert constraints[0]["column_names"] == ["household_id", "source", "fingerprint"]
                migration.downgrade()
                assert "recipe_migrations" not in sa.inspect(connection).get_table_names()
                assert "recipes" in sa.inspect(connection).get_table_names()
    finally:
        engine.dispose()


@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_identity_schema_compiles_for_supported_databases(dialect: str) -> None:
    output = StringIO()
    context = MigrationContext.configure(dialect_name=dialect, opts={"as_sql": True, "output_buffer": output})
    with Operations.context(context):
        migration.upgrade()
        migration.downgrade()
    sql = output.getvalue()
    assert "UNIQUE (household_id, source, fingerprint)" in sql
    assert "ON DELETE CASCADE" in sql
    assert "DROP TABLE recipe_migrations" in sql
