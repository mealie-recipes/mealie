from logging import getLogger

from mealie.db.db_base import BaseDocument
from mealie.db.models.event import Event, EventNotification
from mealie.db.models.group import Group
from mealie.db.models.mealplan import MealPlanModel
from mealie.db.models.recipe.recipe import Category, RecipeModel, Tag
from mealie.db.models.settings import CustomPage, SiteSettings
from mealie.db.models.sign_up import SignUp
from mealie.db.models.theme import SiteThemeModel
from mealie.db.models.users import LongLiveToken, User
from mealie.schema.category import RecipeCategoryResponse, RecipeTagResponse
from mealie.schema.event_notifications import EventNotificationIn
from mealie.schema.events import Event as EventSchema
from mealie.schema.meal import MealPlanInDB
from mealie.schema.recipe import Recipe
from mealie.schema.settings import CustomPageOut
from mealie.schema.settings import SiteSettings as SiteSettingsSchema
from mealie.schema.sign_up import SignUpOut
from mealie.schema.theme import SiteTheme
from mealie.schema.user import GroupInDB, LongLiveTokenInDB, UserInDB
from sqlalchemy.orm.session import Session

logger = getLogger()


class _Recipes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model: RecipeModel = RecipeModel
        self.schema: Recipe = Recipe

    def update_image(self, session: Session, slug: str, extension: str = None) -> str:
        entry: RecipeModel = self._query_one(session, match_value=slug)
        entry.image = f"{slug}.{extension}"
        session.commit()

        return f"{slug}.{extension}"

    def count_uncategorized(self, session: Session, count=True, override_schema=None) -> int:
        return self._countr_attribute(
            session,
            attribute_name=RecipeModel.recipe_category,
            attr_match=None,
            count=count,
            override_schema=override_schema,
        )

    def count_untagged(self, session: Session, count=True, override_schema=None) -> int:
        return self._countr_attribute(
            session, attribute_name=RecipeModel.tags, attr_match=None, count=count, override_schema=override_schema
        )


class _Categories(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model = Category
        self.schema = RecipeCategoryResponse

    def get_empty(self, session: Session):
        return session.query(Category).filter(~Category.recipes.any()).all()


class _Tags(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model = Tag
        self.schema = RecipeTagResponse

    def get_empty(self, session: Session):
        return session.query(Tag).filter(~Tag.recipes.any()).all()


class _Meals(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "uid"
        self.sql_model = MealPlanModel
        self.schema = MealPlanInDB


class _Settings(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = SiteSettings
        self.schema = SiteSettingsSchema


class _Themes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = SiteThemeModel
        self.schema = SiteTheme


class _Users(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = User
        self.schema = UserInDB

    def update_password(self, session, id, password: str):
        entry = self._query_one(session=session, match_value=id)
        entry.update_password(password)
        session.commit()

        return self.schema.from_orm(entry)


class _LongLiveToken(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = LongLiveToken
        self.schema = LongLiveTokenInDB


class _Groups(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = Group
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

        return group.mealplans


class _SignUps(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "token"
        self.sql_model = SignUp
        self.schema = SignUpOut


class _CustomPages(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = CustomPage
        self.schema = CustomPageOut


class _Events(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = Event
        self.schema = EventSchema


class _EventNotification(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = EventNotification
        self.schema = EventNotificationIn


class Database:
    def __init__(self) -> None:
        self.recipes = _Recipes()
        self.meals = _Meals()
        self.settings = _Settings()
        self.themes = _Themes()
        self.categories = _Categories()
        self.tags = _Tags()
        self.users = _Users()
        self.api_tokens = _LongLiveToken()
        self.sign_ups = _SignUps()
        self.groups = _Groups()
        self.custom_pages = _CustomPages()
        self.events = _Events()
        self.event_notifications = _EventNotification()


db = Database()
