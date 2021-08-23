from mealie.core import root_logger
from mealie.core.config import settings
from mealie.core.security import get_password_hash
from mealie.db.data_initialization.init_units_foods import default_recipe_unit_init
from mealie.db.database import db
from mealie.db.db_setup import create_session, engine
from mealie.db.models._model_base import SqlAlchemyBase
from mealie.schema.admin import SiteSettings, SiteTheme
from mealie.services.events import create_general_event
from sqlalchemy.orm import Session

logger = root_logger.get_logger("init_db")


def create_all_models():
    import mealie.db.models._all_models  # noqa: F401

    SqlAlchemyBase.metadata.create_all(engine)


def init_db(session: Session = None) -> None:
    create_all_models()

    if not session:
        session = create_session()

    default_group_init(session)
    default_settings_init(session)
    default_theme_init(session)
    default_user_init(session)

    default_recipe_unit_init(db, session)

    session.close()


def default_theme_init(session: Session):
    default_themes = [
        SiteTheme().dict(),
        {
            "name": "Dark",
            "colors": {
                "primary": "#424242",
                "accent": "#455A64",
                "secondary": "#00796B",
                "success": "#43A047",
                "info": "#1976D2",
                "warning": "#FF6F00",
                "error": "#EF5350",
            },
        },
    ]
    for theme in default_themes:
        db.themes.create(session, theme)


def default_settings_init(session: Session):
    document = db.settings.create(session, SiteSettings().dict())
    logger.info(f"Created Site Settings: \n {document}")


def default_group_init(session: Session):
    default_group = {"name": settings.DEFAULT_GROUP}
    logger.info("Generating Default Group")
    db.groups.create(session, default_group)


def default_user_init(session: Session):
    default_user = {
        "full_name": "Change Me",
        "email": settings.DEFAULT_EMAIL,
        "password": get_password_hash(settings.DEFAULT_PASSWORD),
        "group": settings.DEFAULT_GROUP,
        "admin": True,
    }

    logger.info("Generating Default User")
    db.users.create(session, default_user)


def main():
    try:
        session = create_session()
        init_user = db.users.get(session, "1", "id")
    except Exception:
        init_db()
        return
    if init_user:
        logger.info("Database Exists")
    else:
        logger.info("Database Doesn't Exists, Initializing...")
        init_db()
        create_general_event("Initialize Database", "Initialize database with default values", session)


if __name__ == "__main__":
    main()
