from settings import USE_MONGO, USE_TINYDB

from db.db_base import BaseDocument
from db.db_setup import USE_MONGO, USE_TINYDB, tiny_db
from db.mongo.settings_models import SiteThemeDocument


class _Themes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        if USE_TINYDB:
            self.store = tiny_db.themes
        self.document = SiteThemeDocument

    def update(self, key: str, new_data: dict) -> dict:
        if USE_MONGO:
            pass
        elif USE_TINYDB:
            pass
