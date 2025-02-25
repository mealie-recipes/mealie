import os
from collections.abc import Callable
from pathlib import Path
from time import sleep

from alembic import command, config, script
from alembic.config import Config
from alembic.runtime import migration
from sqlalchemy import engine, orm, text

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.db.db_setup import session_context
from mealie.db.fixes.fix_group_with_no_name import fix_group_with_no_name
from mealie.db.fixes.fix_migration_data import fix_migration_data
from mealie.db.fixes.fix_slug_foods import fix_slug_food_names
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.repos.seed.init_users import default_user_init
from mealie.schema.household.household import HouseholdCreate, HouseholdInDB
from mealie.schema.user.user import GroupBase, GroupInDB
from mealie.services.group_services.group_service import GroupService
from mealie.services.household_services.household_service import HouseholdService

ALEMBIC_DIR = Path(__file__).parent.parent / "alembic"

logger = root_logger.get_logger()


def init_db(session: orm.Session) -> None:
    settings = get_app_settings()

    instance_repos = get_repositories(session)
    default_group = default_group_init(instance_repos, settings.DEFAULT_GROUP)

    group_repos = get_repositories(session, group_id=default_group.id, household_id=None)
    default_household = group_repos.households.get_by_name(settings.DEFAULT_HOUSEHOLD)
    if default_household is None:
        default_household = default_household_init(group_repos, settings.DEFAULT_HOUSEHOLD)
    household_repos = get_repositories(session, group_id=default_group.id, household_id=default_household.id)
    default_user_init(household_repos)


def default_group_init(repos: AllRepositories, name: str) -> GroupInDB:
    logger.info("Generating Default Group and Household")
    return GroupService.create_group(repos, GroupBase(name=name))


def default_household_init(repos: AllRepositories, name: str) -> HouseholdInDB:
    logger.info("Generating Default Household")
    return HouseholdService.create_household(repos, HouseholdCreate(name=name))


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


def safe_try(func: Callable):
    try:
        func()
    except Exception:
        logger.exception(f"Error calling '{func.__name__}'")


def connect(session: orm.Session) -> bool:
    try:
        session.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Error connecting to database")
        return False


def main():
    # Wait for database to connect
    max_retry = 10
    wait_seconds = 1

    with session_context() as session:
        while True:
            if connect(session):
                logger.info("Database connection established.")
                break

            logger.error(f"Database connection failed. Retrying in {wait_seconds} seconds...")
            max_retry -= 1

            sleep(wait_seconds)

            if max_retry == 0:
                raise ConnectionError("Database connection failed - exiting application.")

        alembic_cfg_path = os.getenv("ALEMBIC_CONFIG_FILE", default=str(ALEMBIC_DIR / "alembic.ini"))

        if not os.path.isfile(alembic_cfg_path):
            raise Exception("Provided alembic config path doesn't exist")

        run_fixes = False
        alembic_cfg = Config(alembic_cfg_path)
        if db_is_at_head(alembic_cfg):
            logger.debug("Migration not needed.")
        else:
            logger.info("Migration needed. Performing migration...")
            command.upgrade(alembic_cfg, "head")
            run_fixes = True

        if session.get_bind().name == "postgresql":  # needed for fuzzy search and fast GIN text indices
            session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

        db = get_repositories(session, group_id=None, household_id=None)

        if db.users.get_all():
            logger.debug("Database exists")
            if run_fixes:
                safe_try(lambda: fix_migration_data(session))
                safe_try(lambda: fix_slug_food_names(db))
                safe_try(lambda: fix_group_with_no_name(session))

        else:
            logger.info("Database contains no users, initializing...")
            init_db(session)


if __name__ == "__main__":
    main()
