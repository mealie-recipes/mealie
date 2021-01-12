import json
from typing import List, Optional

from db.database import db
from db.mongo.settings_models import (
    SiteSettingsDocument,
    SiteThemeDocument,
    ThemeColorsDocument,
    WebhooksDocument,
)
from pydantic import BaseModel
from startup import USE_TINYDB
from utils.logger import logger


class Webhooks(BaseModel):
    webhookTime: str = "00:00"
    webhookURLs: Optional[List[str]] = []
    enabled: bool = "false"


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
    def _unpack_doc(document: SiteSettingsDocument):
        document = json.loads(document.to_json())
        del document["_id"]
        document["webhhooks"] = Webhooks(**document["webhooks"])
        return SiteSettings(**document)

    @staticmethod
    def get_site_settings():
        try:
            document = db.settings.get("main")
        except:
            webhooks = Webhooks()
            default_entry = SiteSettings(name="main", webhooks=webhooks)
            document = db.settings.save_new(default_entry.dict(), webhooks.dict())

        return SiteSettings(**document)

    def update(self):

        db.settings.update(name="main", new_data=self.dict())


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

    @staticmethod
    def get_by_name(theme_name):
        if USE_TINYDB:
            theme = Query()
            document = tinydb.themes.search(theme.name == theme_name)
        else:
            document = SiteThemeDocument.objects.get(name=theme_name)

        return SiteTheme._unpack_doc(document)

    @staticmethod
    def _unpack_doc(document):
        if USE_TINYDB:
            theme_colors = SiteTheme(**document)
        else:
            document = json.loads(document.to_json())
            del document["_id"]
            theme_colors = SiteTheme(**document)

        return theme_colors

    @staticmethod
    def get_all():
        all_themes = []
        for theme in SiteThemeDocument.objects():
            all_themes.append(SiteTheme._unpack_doc(theme))

        return all_themes

    def save_to_db(self):
        if USE_TINYDB:
            self._save_to_tinydb()
        else:
            self._save_to_mongo()

    def _save_to_tinydb(self):
        tinydb.themes.insert(self.dict())

    def _save_to_mongo(self):
        theme = self.dict()
        theme["colors"] = ThemeColorsDocument(**theme["colors"])

        theme_document = SiteThemeDocument(**theme)

        theme_document.save()

    def update_document(self):
        theme = self.dict()
        theme["colors"] = ThemeColorsDocument(**theme["colors"])

        theme_document = SiteThemeDocument.objects.get(name=self.name)

        if theme_document:
            theme_document.update(set__colors=theme["colors"])

        theme_document.save()

    @staticmethod
    def delete_theme(theme_name: str) -> str:
        """ Removes the theme by name """
        document = SiteThemeDocument.objects.get(name=theme_name)

        if document:
            document.delete()
            return "Document Deleted"


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

    if USE_TINYDB:
        theme = Query()
        item = tinydb.themes.search(theme.name == "default")
        print(item)
        if item == []:
            logger.info("Generating Default Theme")
            colors = Colors(**default_colors)
            default_theme = SiteTheme(name="default", colors=colors)
            default_theme.save_to_db()
    else:
        try:
            SiteTheme.get_by_name("default")
            return "default theme exists"
        except:
            logger.info("Generating Default Theme")
            colors = Colors(**default_colors)
            default_theme = SiteTheme(name="default", colors=colors)
            default_theme.save_to_db()


# default_theme_init()
