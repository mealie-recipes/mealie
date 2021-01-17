from app_config import USE_SQL

from db.db_base import BaseDocument
from db.db_setup import USE_SQL
from db.sql.db_session import create_session
from db.sql.theme_models import SiteThemeModel


class _Themes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        self.sql_model = SiteThemeModel
        self.create_session = create_session

    def save_new(self, theme_data: dict) -> None:
        session = self.create_session()
        new_theme = self.sql_model(**theme_data)

        session.add(new_theme)
        session.commit()

        return_data = new_theme.dict()

        session.close()
        return return_data

    def update(self, data: dict) -> dict:
        session, theme_model = self._query_one(
            match_value=data["name"], match_key="name"
        )

        theme_model.update(**data)
        session.commit()
        session.close()
