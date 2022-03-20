from collections.abc import Callable
from pathlib import Path
from time import sleep

from sqlalchemy import engine, orm

from alembic import command, config, script
from alembic.config import Config
from alembic.runtime import migration
from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.db.db_setup import create_session
from mealie.db.fixes.fix_slug_foods import fix_slug_food_names
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.repos.seed.init_users import default_user_init
from mealie.repos.seed.seeders import IngredientFoodsSeeder, IngredientUnitsSeeder, MultiPurposeLabelSeeder
from mealie.schema.user.user import GroupBase
from mealie.services.group_services.group_utils import create_new_group

PROJECT_DIR = Path(__file__).parent.parent.parent

logger = root_logger.get_logger("init_db")


def init_db(db: AllRepositories) -> None:
    # TODO: Port other seed data to use abstract seeder class
    default_group_init(db)
    default_user_init(db)

    group_id = db.groups.get_all()[0].id

    seeders = [
        MultiPurposeLabelSeeder(db, group_id=group_id),
        IngredientFoodsSeeder(db, group_id=group_id),
        IngredientUnitsSeeder(db, group_id=group_id),
    ]

    for seeder in seeders:
        seeder.seed()


def default_group_init(db: AllRepositories):
    settings = get_app_settings()

    logger.info("Generating Default Group")
    create_new_group(db, GroupBase(name=settings.DEFAULT_GROUP))


# Adapted from https://alembic.sqlalchemy.org/en/latest/cookbook.html#test-current-database-revision-is-at-head-s
def db_is_at_head(alembic_cfg: config.Config) -> bool:
    settings = get_app_settings()
    url = settings.DB_URL

    if not url:
        raise ValueError("No database url found")

    connectable = engine.create_engine(url)
    directory = script.ScriptDirectory.from_config(alembic_cfg)
    with connectable.begin() as connection:
        context = migration.MigrationContext.configure(connection)
        return set(context.get_current_heads()) == set(directory.get_heads())


def safe_try(name: str, func: Callable):
    try:
        func()
    except Exception as e:
        logger.error(f"Error calling '{name}': {e}")


def connect(session: orm.Session) -> bool:
    try:
        session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return False


def main():
    session = create_session()

    # Wait for database to connect
    max_retry = 10
    wait_seconds = 1

    while True:
        if connect(session):
            logger.info("Database connection established.")
            break

        logger.error(f"Database connection failed. Retrying in {wait_seconds} seconds...")
        max_retry -= 1

        sleep(wait_seconds)

        if max_retry == 0:
            raise ConnectionError("Database connection failed - exiting application.")

    alembic_cfg = Config(str(PROJECT_DIR / "alembic.ini"))
    if db_is_at_head(alembic_cfg):
        logger.info("Migration not needed.")
    else:
        logger.info("Migration needed. Performing migration...")
        command.upgrade(alembic_cfg, "head")

    db = get_repositories(session)

    init_user = db.users.get_all()
    if init_user:
        logger.info("Database exists")
    else:
        logger.info("Database contains no users, initializing...")
        init_db(db)

    safe_try("fix slug food names", lambda: fix_slug_food_names(db))


if __name__ == "__main__":
    main()
