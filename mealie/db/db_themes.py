from settings import USE_MONGO, USE_TINYDB

from db.db_base import BaseDocument
from db.db_setup import USE_MONGO, USE_TINYDB, tiny_db
from db.mongo.settings_models import SiteThemeDocument, ThemeColorsDocument


class _Themes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        if USE_TINYDB:
            self.store = tiny_db.themes
        self.document = SiteThemeDocument

    def save_new(self, theme_data: dict) -> None:
        if USE_MONGO:
            theme_data["colors"] = ThemeColorsDocument(**theme_data["colors"])

            document = self.document(**theme_data)

            document.save()
        elif USE_TINYDB:
            pass

    def update(self, data: dict) -> dict:
        if USE_MONGO:
            colors = ThemeColorsDocument(**data["colors"])
            theme_document = self.document.objects.get(name=data.get("name"))

            if theme_document:
                theme_document.update(set__colors=colors)
                theme_document.save()
            else:
                raise Exception("No database entry was found to update")

        elif USE_TINYDB:
            pass
