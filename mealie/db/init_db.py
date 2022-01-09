from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.db.db_setup import create_session, engine
from mealie.db.models._model_base import SqlAlchemyBase
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.repos.seed.seeders import IngredientFoodsSeeder, IngredientUnitsSeeder, MultiPurposeLabelSeeder
from mealie.repos.seed.init_users import default_user_init
from mealie.schema.user.user import GroupBase
from mealie.services.events import create_general_event
from mealie.services.group_services.group_utils import create_new_group

logger = root_logger.get_logger("init_db")


def create_all_models():
    import mealie.db.models._all_models  # noqa: F401
    SqlAlchemyBase.metadata.create_all(engine)


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
    create_all_models()

    session = create_session()
    db = get_repositories(session)

    try:
        init_user = db.users.get_all()
        if not init_user:
            raise Exception("No users found in database")
    except Exception:
        init_db(db)
        return

    if init_user:
        logger.info("Database Exists")
    else:
        logger.info("Database Doesn't Exists, Initializing...")
        init_db(db)
        create_general_event("Initialize Database", "Initialize database with default values", session)


if __name__ == "__main__":
    main()
