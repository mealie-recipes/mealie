from settings import USE_MONGO, USE_SQL

from db.db_base import BaseDocument
from db.db_setup import USE_MONGO, USE_SQL
from db.mongo.settings_models import SiteThemeDocument, ThemeColorsDocument
from db.sql.db_session import create_session
from db.sql.settings_models import SiteThemeModel, ThemeColorsModel


class _Themes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        if USE_SQL:
            self.sql_model = SiteThemeModel
        else:
            self.document = SiteThemeDocument

    def save_new(self, theme_data: dict) -> None:
        if USE_MONGO:
            theme_data["colors"] = ThemeColorsDocument(**theme_data["colors"])

            document = self.document(**theme_data)

            document.save()
        elif USE_SQL:
            session = create_session()

            colors = ThemeColorsModel()
            new_colors = theme_data.get("colors")
            colors.primary = new_colors.get("primary")
            colors.secondary = new_colors.get("secondary")
            colors.accent = new_colors.get("accent")
            colors.success = new_colors.get("success")
            colors.info = new_colors.get("info")
            colors.warning = new_colors.get("warning")
            colors.error = new_colors.get("error")

            new_theme = self.sql_model(name=theme_data.get("name"))

            new_theme.colors = colors

            session.add(new_theme)
            session.commit()
            
            return

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
            pass
