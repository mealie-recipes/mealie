from typing import List, Optional

from db.database import db
from db.db_setup import sql_exists
from db.db_setup import create_session, generate_session
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from utils.logger import logger


class Webhooks(BaseModel):
    webhookTime: str = "00:00"
    webhookURLs: Optional[List[str]] = []
    enabled: bool = False


class SiteSettings(BaseModel):
    name: str = "main"
    webhooks: Webhooks

    class Config:
        schema_extra = {
            "example": {
                "name": "main",
                "webhooks": {
                    "webhookTime": "00:00",
                    "webhookURLs": ["https://mywebhookurl.com/webhook"],
                    "enable": False,
                },
            }
        }

    @staticmethod
    def get_all(session: Session):
        db.settings.get_all(session)

    @classmethod
    def get_site_settings(cls, session: Session):
        try:
            document = db.settings.get(session=session, match_value="main")
        except:
            webhooks = Webhooks()
            default_entry = SiteSettings(name="main", webhooks=webhooks)
            document = db.settings.save_new(
                session, default_entry.dict(), webhooks.dict()
            )

        return cls(**document)

    def update(self):
        db.settings.update("main", new_data=self.dict())


class Colors(BaseModel):
    primary: str
    accent: str
    secondary: str
    success: str
    info: str
    warning: str
    error: str


class SiteTheme(BaseModel):
    name: str
    colors: Colors

    class Config:
        schema_extra = {
            "example": {
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
        }

    @classmethod
    def get_by_name(cls, session: Session, theme_name):
        db_entry = db.themes.get(session, theme_name)
        name = db_entry.get("name")
        colors = Colors(**db_entry.get("colors"))

        return cls(name=name, colors=colors)

    @staticmethod
    def get_all(session: Session):
        all_themes = db.themes.get_all(session)
        for index, theme in enumerate(all_themes):
            name = theme.get("name")
            colors = Colors(**theme.get("colors"))

            all_themes[index] = SiteTheme(name=name, colors=colors)

        return all_themes

    def save_to_db(self, session: Session):
        db.themes.save_new(session, self.dict())

    def update_document(self, session: Session):
        db.themes.update(session, self.dict())

    @staticmethod
    def delete_theme(session: Session, theme_name: str) -> str:
        """ Removes the theme by name """
        db.themes.delete(session, theme_name)


def default_theme_init():
    default_colors = {
        "primary": "#E58325",
        "accent": "#00457A",
        "secondary": "#973542",
        "success": "#5AB1BB",
        "info": "#4990BA",
        "warning": "#FF4081",
        "error": "#EF5350",
    }
    session = create_session()
    try:
        SiteTheme.get_by_name(session, "default")
        logger.info("Default theme exists... skipping generation")
    except:
        logger.info("Generating Default Theme")
        colors = Colors(**default_colors)
        default_theme = SiteTheme(name="default", colors=colors)
        default_theme.save_to_db(session)


def default_settings_init():
    session = create_session()
    try:
        document = db.settings.get(session, "main")
    except:
        webhooks = Webhooks()
        default_entry = SiteSettings(name="main", webhooks=webhooks)
        document = db.settings.save_new(session, default_entry.dict(), webhooks.dict())


if not sql_exists:
    default_settings_init()
    default_theme_init()
