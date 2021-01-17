from app_config import USE_SQL

from db.db_base import BaseDocument
from db.db_setup import USE_SQL
from db.sql.db_session import create_session
from db.sql.settings_models import SiteSettingsModel


class _Settings(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        self.sql_model = SiteSettingsModel
        self.create_session = create_session

    def save_new(self, main: dict, webhooks: dict) -> str:
        session = create_session()
        new_settings = self.sql_model(main.get("name"), webhooks)

        session.add(new_settings)
        session.commit()

        return new_settings.dict()
