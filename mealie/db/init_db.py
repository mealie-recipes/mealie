from core.config import DEFAULT_GROUP
from core.security import get_password_hash
from fastapi.logger import logger
from schema.settings import SiteSettings
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import Session

from db.database import db
from db.db_setup import create_session


def init_db(db: Session = None) -> None:
    if not db:
        db = create_session()

    default_group_init(db)
    default_settings_init(db)
    default_theme_init(db)
    default_user_init(db)

    db.close()


def default_theme_init(session: Session):
    default_theme = {
        "name": "default",
        "colors": {
            "primary": "#E58325",
            "accent": "#00457A",
            "secondary": "#973542",
            "success": "#5AB1BB",
            "info": "#4990BA",
            "warning": "#FF4081",
            "error": "#EF5350",
        },
    }

    try:
        db.themes.create(session, default_theme)
        logger.info("Generating default theme...")
    except:
        logger.info("Default Theme Exists.. skipping generation")


def default_settings_init(session: Session):
    data = {"language": "en", "sidebar": {"categories": []}}
    document = db.settings.create(session, data)
    logger.info(f"Created Site Settings: \n {document}")


def default_group_init(session: Session):
    default_group = {"name": DEFAULT_GROUP}
    logger.info("Generating Default Group")
    db.groups.create(session, default_group)
    pass


def default_user_init(session: Session):
    default_user = {
        "full_name": "Change Me",
        "email": "changeme@email.com",
        "password": get_password_hash("MyPassword"),
        "group": DEFAULT_GROUP,
        "admin": True,
    }

    logger.info("Generating Default User")
    db.users.create(session, default_user)
