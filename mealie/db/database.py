from schema.category import RecipeCategoryResponse
from schema.meal import MealPlanInDB
from schema.recipe import Recipe
from schema.settings import SiteSettings as SiteSettingsSchema
from schema.sign_up import SignUpOut
from schema.theme import SiteTheme
from schema.user import GroupInDB, UserInDB
from sqlalchemy.orm.session import Session

from db.db_base import BaseDocument
from db.models.group import Group
from db.models.mealplan import MealPlanModel
from db.models.recipe.recipe import Category, RecipeModel, Tag
from db.models.settings import SiteSettings
from db.models.sign_up import SignUp
from db.models.theme import SiteThemeModel
from db.models.users import User


class _Recipes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model: RecipeModel = RecipeModel
        self.orm_mode = True
        self.schema: Recipe = Recipe

    def update_image(self, session: Session, slug: str, extension: str = None) -> str:
        entry: RecipeModel = self._query_one(session, match_value=slug)
        entry.image = f"{slug}.{extension}"
        session.commit()

        return f"{slug}.{extension}"


class _Categories(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model = Category
        self.orm_mode = True
        self.schema = RecipeCategoryResponse


class _Tags(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model = Tag
        self.orm_mode = False


class _Meals(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "uid"
        self.sql_model = MealPlanModel
        self.orm_mode = True
        self.schema = MealPlanInDB


class _Settings(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = SiteSettings
        self.orm_mode = True
        self.schema = SiteSettingsSchema


class _Themes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "name"
        self.sql_model = SiteThemeModel
        self.orm_mode = True
        self.schema = SiteTheme


class _Users(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = User
        self.orm_mode = True
        self.schema = UserInDB

    def update_password(self, session, id, password: str):
        entry = self._query_one(session=session, match_value=id)
        entry.update_password(password)
        session.commit()

        return self.schema.from_orm(entry)


class _Groups(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = Group
        self.orm_mode = True
        self.schema = GroupInDB


class _SignUps(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "token"
        self.sql_model = SignUp
        self.orm_mode = True
        self.schema = SignUpOut


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
        self.groups = _Groups()


db = Database()
