from mealie.core import root_logger
from mealie.core.config import get_settings
from mealie.db.data_access_layer.access_model_factory import Database
from mealie.db.data_initialization.init_units_foods import default_recipe_unit_init
from mealie.db.data_initialization.init_users import default_user_init
from mealie.db.database import get_database
from mealie.db.db_setup import create_session, engine
from mealie.db.models._model_base import SqlAlchemyBase
from mealie.schema.admin import SiteSettings
from mealie.schema.user.user import GroupBase
from mealie.services.events import create_general_event
from mealie.services.group_services.group_utils import create_new_group

logger = root_logger.get_logger("init_db")

settings = get_settings()


def create_all_models():
    import mealie.db.models._all_models  # noqa: F401

    SqlAlchemyBase.metadata.create_all(engine)


def init_db(db: Database) -> None:
    default_group_init(db)
    default_settings_init(db)
    default_user_init(db)
    default_recipe_unit_init(db)


def default_settings_init(db: Database):
    document = db.settings.create(SiteSettings().dict())
    logger.info(f"Created Site Settings: \n {document}")


def default_group_init(db: Database):
    logger.info("Generating Default Group")
    create_new_group(db, GroupBase(name=settings.DEFAULT_GROUP))


def main():
    create_all_models()

    session = create_session()
    db = get_database(session)

    try:
        init_user = db.users.get("1", "id")
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
