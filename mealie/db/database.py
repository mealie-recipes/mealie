from mealie.db.db_base import BaseDocument
from mealie.db.models.group import Group
from mealie.db.models.mealplan import MealPlanModel
from mealie.db.models.recipe.recipe import Category, RecipeModel, Tag
from mealie.db.models.settings import CustomPage, SiteSettings
from mealie.db.models.sign_up import SignUp
from mealie.db.models.theme import SiteThemeModel
from mealie.db.models.users import User
from mealie.schema.category import RecipeCategoryResponse, RecipeTagResponse
from mealie.schema.meal import MealPlanInDB
from mealie.schema.recipe import Recipe
from mealie.schema.settings import CustomPageOut, SiteSettings as SiteSettingsSchema
from mealie.schema.sign_up import SignUpOut
from mealie.schema.theme import SiteTheme
from mealie.schema.user import GroupInDB, UserInDB
from sqlalchemy.orm.session import Session


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
        self.orm_mode = True
        self.schema = RecipeTagResponse


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

    def get_meals(self, session: Session, match_value: str, match_key: str = "name") -> list[MealPlanInDB]:
        """A Helper function to get the group from the database and return a sorted list of

        Args:
            session (Session): SqlAlchemy Session
            match_value (str): Match Value
            match_key (str, optional): Match Key. Defaults to "name".

        Returns:
            list[MealPlanInDB]: [description]
        """
        group: GroupInDB = session.query(self.sql_model).filter_by(**{match_key: match_value}).one_or_none()

        # Potentially not needed? column is sorted by SqlAlchemy based on startDate
        # return sorted(group.mealplans, key=lambda mealplan: mealplan.startDate)
        return group.mealplans


class _SignUps(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "token"
        self.sql_model = SignUp
        self.orm_mode = True
        self.schema = SignUpOut

class _CustomPages(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = CustomPage
        self.orm_mode = True
        self.schema = CustomPageOut


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
        self.custom_pages = _CustomPages()


db = Database()
