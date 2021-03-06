from sqlalchemy.orm.session import Session

from db.db_base import BaseDocument
from db.models.mealplan import MealPlanModel
from db.models.recipe import Category, RecipeModel, Tag
from db.models.settings import SiteSettingsModel
from db.models.sign_up import SignUp
from db.models.theme import SiteThemeModel
from db.models.users import User

"""
# TODO
    - [ ] Abstract Classes to use save_new, and update from base models
"""


class _Recipes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model: RecipeModel = RecipeModel

    def update_image(self, session: Session, slug: str, extension: str = None) -> str:
        entry: RecipeModel = self._query_one(session, match_value=slug)
        entry.image = f"{slug}.{extension}"
        session.commit()

        return f"{slug}.{extension}"


class _Categories(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model = Category


class _Tags(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model = Tag


class _Meals(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "uid"
        self.sql_model = MealPlanModel


class _Settings(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        self.sql_model = SiteSettingsModel


class _Themes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        self.sql_model = SiteThemeModel


class _Users(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = User

    def update_password(self, session, id, password: str):
        entry = self._query_one(session=session, match_value=id)
        entry.update_password(password)
        return_data = entry.dict()
        session.commit()

        return return_data


class _SignUps(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "token"
        self.sql_model = SignUp


class _SignUps(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "token"
        self.sql_model = SignUp


class Database:
    def __init__(self) -> None:
        self.recipes = _Recipes()
        self.meals = _Meals()
        self.settings = _Settings()
        self.themes = _Themes()
        self.categories = _Categories()
        self.tags = _Tags()
        self.users = _Users()
        self.sign_ups = _SignUps()


db = Database()
