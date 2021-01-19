from db.db_base import BaseDocument
from db.sql.meal_models import MealPlanModel
from db.sql.recipe_models import RecipeModel
from db.sql.settings_models import SiteSettingsModel
from db.sql.theme_models import SiteThemeModel

"""
# TODO
    - [ ] Abstract Classes to use save_new, and update from base models
    - [ ] Create Category and Tags Table with Many to Many relationship
"""


class _Recipes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model = RecipeModel

    def update_image(self, slug: str, extension: str) -> None:
        pass


class _Meals(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "uid"
        self.sql_model = MealPlanModel


class _Settings(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        self.sql_model = SiteSettingsModel

    def save_new(self, session, main: dict, webhooks: dict) -> str:
        new_settings = self.sql_model(main.get("name"), webhooks)

        session.add(new_settings)
        session.commit()

        return new_settings.dict()


class _Themes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        self.sql_model = SiteThemeModel

    def update(self, session, data: dict) -> dict:
        theme_model = self._query_one(
            session=session, match_value=data["name"], match_key="name"
        )

        theme_model.update(**data)
        session.commit()


class Database:
    def __init__(self) -> None:
        self.recipes = _Recipes()
        self.meals = _Meals()
        self.settings = _Settings()
        self.themes = _Themes()


db = Database()
