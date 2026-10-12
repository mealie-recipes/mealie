import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file


def _migration():
    path = next(ALEMBIC_MIGRATIONS.glob("*a8f3b2c1d4e5*.py"))
    return import_file("add_recipe_scale_to_meal_plan", path)


def _columns(connection: sa.Connection) -> set[str]:
    return {column["name"] for column in sa.inspect(connection).get_columns("group_meal_plans")}


def test_recipe_scale_migration_is_the_latest_revision() -> None:
    """Databases that already ran every earlier revision only pick the column up if it comes last."""
    latest = sorted(ALEMBIC_MIGRATIONS.glob("*.py"))[-1]
    revisions = {
        import_file("alembic_version", path).revision for path in ALEMBIC_MIGRATIONS.glob("*.py") if path != latest
    }

    migration = _migration()
    assert migration.down_revision in revisions
    assert not any(
        import_file("alembic_version", path).down_revision == migration.revision
        for path in ALEMBIC_MIGRATIONS.glob("*.py")
    ), "an existing revision was re-pointed at the recipe_scale migration"


def test_recipe_scale_migration_backfills_existing_entries() -> None:
    migration = _migration()
    engine = sa.create_engine("sqlite://")

    try:
        with engine.connect() as connection:
            connection.execute(
                sa.text("CREATE TABLE group_meal_plans (id INTEGER PRIMARY KEY, title VARCHAR NOT NULL)")
            )
            connection.execute(
                sa.text("INSERT INTO group_meal_plans (id, title) VALUES (1, 'planned before the upgrade')")
            )

            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()

            assert "recipe_scale" in _columns(connection)

            # entries written by something that doesn't know about the column still get a scale
            connection.execute(
                sa.text("INSERT INTO group_meal_plans (id, title) VALUES (2, 'planned after the upgrade')")
            )
            scales = (
                connection.execute(sa.text("SELECT recipe_scale FROM group_meal_plans ORDER BY id")).scalars().all()
            )
            assert scales == [1.0, 1.0]

            with Operations.context(MigrationContext.configure(connection)):
                migration.downgrade()

            assert "recipe_scale" not in _columns(connection)
            assert connection.execute(sa.text("SELECT COUNT(*) FROM group_meal_plans")).scalar_one() == 2
    finally:
        engine.dispose()
