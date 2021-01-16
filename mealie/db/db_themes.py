from settings import USE_MONGO, USE_SQL

from db.db_base import BaseDocument
from db.db_setup import USE_MONGO, USE_SQL
from db.mongo.settings_models import SiteThemeDocument, ThemeColorsDocument
from db.sql.db_session import create_session
from db.sql.theme_models import SiteThemeModel


class _Themes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        if USE_SQL:
            self.sql_model = SiteThemeModel
            self.create_session = create_session
        else:
            self.document = SiteThemeDocument

    def save_new(self, theme_data: dict) -> None:
        if USE_MONGO:
            theme_data["colors"] = ThemeColorsDocument(**theme_data["colors"])

            document = self.document(**theme_data)

            document.save()
        elif USE_SQL:
            session = self.create_session()
            new_theme = self.sql_model(**theme_data)

            session.add(new_theme)
            session.commit()

            return_data = new_theme.dict()

            session.close()
            return return_data

    def update(self, data: dict) -> dict:
        if USE_MONGO:
            colors = ThemeColorsDocument(**data["colors"])
            theme_document = self.document.objects.get(name=data.get("name"))

            if theme_document:
                theme_document.update(set__colors=colors)
                theme_document.save()
            else:
                raise Exception("No database entry was found to update")

        elif USE_SQL:
            session, theme_model = self._query_one(
                match_value=data["name"], match_key="name"
            )

            theme_model.update(**data)
            session.commit()
            session.close()
