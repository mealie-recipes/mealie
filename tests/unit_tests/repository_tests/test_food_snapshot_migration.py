import importlib.util
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


def test_food_snapshot_migration_preserves_existing_rows():
    path = Path("mealie/alembic/versions/2026-09-24-00.00.00_8e2a6621f001_preserve_deleted_foods.py")
    spec = importlib.util.spec_from_file_location("food_snapshot_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        for name in ("recipes_ingredients", "shopping_list_items"):
            connection.exec_driver_sql(f"CREATE TABLE {name} (id INTEGER PRIMARY KEY, note TEXT)")
            connection.exec_driver_sql(f"INSERT INTO {name} (id, note) VALUES (1, 'diced')")
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()
        for name in ("recipes_ingredients", "shopping_list_items"):
            assert connection.exec_driver_sql(f"SELECT note, food_snapshot FROM {name}").one() == ("diced", None)
        migration.downgrade()
        for name in ("recipes_ingredients", "shopping_list_items"):
            assert connection.exec_driver_sql(f"SELECT note FROM {name}").scalar_one() == "diced"
    engine.dispose()
