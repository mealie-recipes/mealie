from mealie.core.config import DEFAULT_GROUP
from mealie.core.security import get_password_hash
from fastapi.logger import logger
from mealie.schema.settings import SiteSettings
from mealie.schema.theme import SiteTheme
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import Session

from mealie.db.database import db
from mealie.db.db_setup import create_session


def init_db(db: Session = None) -> None:
    if not db:
        db = create_session()

    default_group_init(db)
    default_settings_init(db)
    default_theme_init(db)
    default_user_init(db)

    db.close()


def default_theme_init(session: Session):
    db.themes.create(session, SiteTheme().dict())

    try:
        logger.info("Generating default theme...")
    except:
        logger.info("Default Theme Exists.. skipping generation")


def default_settings_init(session: Session):
    data = {"language": "en", "home_page_settings": {"categories": []}}
    document = db.settings.create(session, SiteSettings().dict())
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
