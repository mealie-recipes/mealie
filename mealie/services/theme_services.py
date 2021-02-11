from db.database import db
from db.db_setup import create_session, sql_exists
from utils.logger import logger


def default_theme_init():
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
    session = create_session()
    try:
        db.themes.create(session, default_theme)
        logger.info("Generating default theme...")
    except:
        logger.info("Default Theme Exists.. skipping generation")


if not sql_exists:
    default_theme_init()
