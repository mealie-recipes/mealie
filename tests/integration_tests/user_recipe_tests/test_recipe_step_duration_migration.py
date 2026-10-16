"""Run only against the isolated databases configured by the canonical test harness."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import MetaData, create_engine, inspect, select, text

from mealie.core.config import get_app_settings


def test_duration_migration_preserves_populated_database(random_recipe, unique_user):
    # Release fixture read transactions before PostgreSQL ALTER TABLE locks.
    unique_user.repos.recipes.session.commit()
    unique_user.repos.recipes.session.close()
    settings = get_app_settings()
    engine = create_engine(settings.DB_URL)
    config = Config(str(Path(__file__).parents[3] / "mealie/alembic/alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    assert scripts.get_heads() == ["afdc42353aa4"]
    predecessor = scripts.get_revision("afdc42353aa4").down_revision

    def snapshot():
        metadata = MetaData()
        metadata.reflect(engine)
        with engine.connect() as connection:
            return {
                name: sorted((tuple(map(str, row)) for row in connection.execute(select(table))), key=repr)
                for name, table in metadata.tables.items()
                if name != "alembic_version"
            }

    try:
        command.downgrade(config, predecessor)
        before = snapshot()
        assert before["recipe_instructions"]
        command.upgrade(config, "head")
        column = next(c for c in inspect(engine).get_columns("recipe_instructions") if c["name"] == "duration_seconds")
        assert column["nullable"]
        with engine.begin() as connection:
            assert (
                connection.scalar(text("SELECT COUNT(*) FROM recipe_instructions WHERE duration_seconds IS NOT NULL"))
                == 0
            )
            connection.execute(text("UPDATE recipe_instructions SET duration_seconds = 90"))
        command.downgrade(config, predecessor)
        assert snapshot() == before
        with engine.begin() as connection:
            connection.execute(text("UPDATE recipe_instructions SET text = 'Legacy edit after downgrade'"))
        after_legacy_edit = snapshot()
        command.upgrade(config, "head")
        with engine.connect() as connection:
            assert (
                connection.scalar(text("SELECT COUNT(*) FROM recipe_instructions WHERE duration_seconds IS NOT NULL"))
                == 0
            )
        command.downgrade(config, predecessor)
        assert snapshot() == after_legacy_edit
    finally:
        command.upgrade(config, "head")
        engine.dispose()
