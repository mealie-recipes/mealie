import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file


def _migration():
    path = next(ALEMBIC_MIGRATIONS.glob("*127804c19431*.py"))
    return import_file("drop_recipe_cook_time", path)


ROWS = [
    # id, perform_time, perform_time_seconds, cook_time
    ("only-cook-time", None, None, "20 minutes"),
    ("blank-perform-time", "  ", None, "PT15M"),
    ("has-perform-time", "10 minutes", None, "1 hour"),
    ("has-perform-seconds", None, 600, "1 hour"),
    ("cook-time-none", None, None, " None "),
    ("cook-time-blank", None, None, " "),
    ("nothing", None, None, None),
]


def test_migration_moves_legacy_cook_time_and_drops_column() -> None:
    engine = sa.create_engine("sqlite://")
    try:
        with engine.connect() as connection:
            connection.execute(
                sa.text(
                    "CREATE TABLE recipes (id VARCHAR PRIMARY KEY, perform_time VARCHAR, "
                    "perform_time_seconds INTEGER, cook_time VARCHAR)"
                )
            )
            for row in ROWS:
                connection.execute(
                    sa.text("INSERT INTO recipes VALUES (:a, :b, :c, :d)"), dict(zip("abcd", row, strict=True))
                )

            with Operations.context(MigrationContext.configure(connection)):
                _migration().upgrade()

            columns = {column["name"] for column in sa.inspect(connection).get_columns("recipes")}
            perform_times = {
                row.id: row.perform_time for row in connection.execute(sa.text("SELECT id, perform_time FROM recipes"))
            }
    finally:
        engine.dispose()

    assert "cook_time" not in columns
    assert perform_times == {
        "only-cook-time": "20 minutes",
        "blank-perform-time": "PT15M",
        "has-perform-time": "10 minutes",
        "has-perform-seconds": None,
        "cook-time-none": None,
        "cook-time-blank": None,
        "nothing": None,
    }
