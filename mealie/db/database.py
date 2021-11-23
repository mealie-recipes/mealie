from logging import getLogger
from random import randint

from mealie.db.db_base import BaseDocument
from mealie.db.models.event import Event, EventNotification
from mealie.db.models.group import Group
from mealie.db.models.mealplan import MealPlan
from mealie.db.models.recipe.comment import RecipeComment
from mealie.db.models.recipe.ingredient import IngredientFood, IngredientUnit
from mealie.db.models.recipe.recipe import Category, RecipeModel, Tag
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.db.models.settings import CustomPage, SiteSettings
from mealie.db.models.shopping_list import ShoppingList
from mealie.db.models.sign_up import SignUp
from mealie.db.models.theme import SiteThemeModel
from mealie.db.models.users import LongLiveToken, User
from mealie.schema.category import RecipeCategoryResponse, RecipeTagResponse
from mealie.schema.comments import CommentOut
from mealie.schema.event_notifications import EventNotificationIn
from mealie.schema.events import Event as EventSchema
from mealie.schema.meal import MealPlanOut
from mealie.schema.recipe import Recipe, RecipeIngredientFood, RecipeIngredientUnit
from mealie.schema.settings import CustomPageOut
from mealie.schema.settings import SiteSettings as SiteSettingsSchema
from mealie.schema.shopping_list import ShoppingListOut
from mealie.schema.sign_up import SignUpOut
from mealie.schema.theme import SiteTheme
from mealie.schema.user import GroupInDB, LongLiveTokenInDB, UserInDB
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

logger = getLogger()


class _Recipes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model: RecipeModel = RecipeModel
        self.schema: Recipe = Recipe

    def get_all_not_private(
        self, session: Session, limit: int = None, order_by: str = None, start=0, override_schema=None
    ):
        eff_schema = override_schema or self.schema

        if order_by:
            order_attr = getattr(self.sql_model, str(order_by))

            return [
                eff_schema.from_orm(x)
                for x in session.query(self.sql_model)
                .join(RecipeSettings)
                .filter(RecipeSettings.public == True)  # noqa: 711
                .order_by(order_attr.desc())
                .offset(start)
                .limit(limit)
                .all()
            ]

        return [
            eff_schema.from_orm(x)
            for x in session.query(self.sql_model)
            .join(RecipeSettings)
            .filter(RecipeSettings.public == True)  # noqa: 711
            .offset(start)
            .limit(limit)
            .all()
        ]

    def update_image(self, session: Session, slug: str, _: str = None) -> str:
        entry: RecipeModel = self._query_one(session, match_value=slug)
        entry.image = randint(0, 255)
        session.commit()

        return entry.image

    def count_uncategorized(self, session: Session, count=True, override_schema=None) -> int:
        return self._count_attribute(
            session,
            attribute_name=RecipeModel.recipe_category,
            attr_match=None,
            count=count,
            override_schema=override_schema,
        )

    def count_untagged(self, session: Session, count=True, override_schema=None) -> int:
        return self._count_attribute(
            session, attribute_name=RecipeModel.tags, attr_match=None, count=count, override_schema=override_schema
        )


class _IngredientFoods(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = IngredientFood
        self.schema = RecipeIngredientFood


class _IngredientUnits(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = IngredientUnit
        self.schema = RecipeIngredientUnit


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
        self.sql_model = MealPlan
        self.schema = MealPlanOut


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

    def get_user(self, session: Session, match_key, match_value) -> User:
        try:
            return self._query_one(session, match_key=match_key, match_value=match_value)
        except NoResultFound:           
            return None

    def update_password(self, session, id, password: str):
        entry = self._query_one(session=session, match_value=id)
        entry.update_password(password)
        session.commit()

        return self.schema.from_orm(entry)


class _Comments(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = RecipeComment
        self.schema = CommentOut


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

    def get_meals(self, session: Session, match_value: str, match_key: str = "name") -> list[MealPlanOut]:
        """A Helper function to get the group from the database and return a sorted list of

        Args:
            session (Session): SqlAlchemy Session
            match_value (str): Match Value
            match_key (str, optional): Match Key. Defaults to "name".

        Returns:
            list[MealPlanOut]: [description]
        """
        group: GroupInDB = session.query(self.sql_model).filter_by(**{match_key: match_value}).one_or_none()

        return group.mealplans


class _ShoppingList(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "id"
        self.sql_model = ShoppingList
        self.schema = ShoppingListOut


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
        # Recipes
        self.recipes = _Recipes()
        self.ingredient_foods = _IngredientUnits()
        self.ingredient_units = _IngredientFoods()
        self.categories = _Categories()
        self.tags = _Tags()
        self.comments = _Comments()

        # Site
        self.settings = _Settings()
        self.themes = _Themes()
        self.sign_ups = _SignUps()
        self.custom_pages = _CustomPages()
        self.event_notifications = _EventNotification()
        self.events = _Events()

        # Users / Groups
        self.users = _Users()
        self.api_tokens = _LongLiveToken()
        self.groups = _Groups()
        self.meals = _Meals()
        self.shopping_lists = _ShoppingList()


db = Database()
