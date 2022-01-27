from pathlib import Path

from alembic import command
from alembic.config import Config
from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.db.db_setup import create_session
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.repos.seed.init_users import default_user_init
from mealie.repos.seed.seeders import IngredientFoodsSeeder, IngredientUnitsSeeder, MultiPurposeLabelSeeder
from mealie.schema.user.user import GroupBase
from mealie.services.events import create_general_event
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


def main():
    # TODO Only run migrations if needed?
    alembic_cfg = Config(str(PROJECT_DIR / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")

    session = create_session()
    db = get_repositories(session)

    init_user = db.users.get_all()
    if init_user:
        logger.info("Database exists")
    else:
        logger.info("Database contains no users, initializing...")
        init_db(db)
        create_general_event("Initialize Database", "Initialize database with default values", session)


if __name__ == "__main__":
    main()
