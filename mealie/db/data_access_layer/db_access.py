from logging import getLogger

from mealie.db.data_access_layer.group_access_model import GroupDataAccessModel
from mealie.db.models.event import Event, EventNotification
from mealie.db.models.group import Group
from mealie.db.models.mealplan import MealPlan
from mealie.db.models.recipe.comment import RecipeComment
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
from mealie.db.models.recipe.recipe import Category, RecipeModel, Tag
from mealie.db.models.settings import CustomPage, SiteSettings
from mealie.db.models.shopping_list import ShoppingList
from mealie.db.models.sign_up import SignUp
from mealie.db.models.theme import SiteThemeModel
from mealie.db.models.users import LongLiveToken, User
from mealie.schema.admin import CustomPageOut
from mealie.schema.admin import SiteSettings as SiteSettingsSchema
from mealie.schema.admin import SiteTheme
from mealie.schema.events import Event as EventSchema
from mealie.schema.events import EventNotificationIn
from mealie.schema.meal_plan import MealPlanOut, ShoppingListOut
from mealie.schema.recipe import (
    CommentOut,
    IngredientFood,
    IngredientUnit,
    Recipe,
    RecipeCategoryResponse,
    RecipeTagResponse,
)
from mealie.schema.user import GroupInDB, LongLiveTokenInDB, SignUpOut, UserInDB
from sqlalchemy.orm.session import Session

from ._base_access_model import BaseAccessModel
from .recipe_access_model import RecipeDataAccessModel
from .user_access_model import UserDataAccessModel

logger = getLogger()


DEFAULT_PK = "id"


class CategoryDataAccessModel(BaseAccessModel):
    def get_empty(self, session: Session):
        self.schema
        return session.query(Category).filter(~Category.recipes.any()).all()


class TagsDataAccessModel(BaseAccessModel):
    def get_empty(self, session: Session):
        return session.query(Tag).filter(~Tag.recipes.any()).all()


class DatabaseAccessLayer:
    """
    `DatabaseAccessLayer` class is the data access layer for all database actions within
    Mealie. Database uses composition from classes derived from BaseAccessModel. These
    can be substantiated from the BaseAccessModel class or through inheritance when
    additional methods are required.
    """

    def __init__(self) -> None:

        # Recipes
        self.recipes = RecipeDataAccessModel("slug", RecipeModel, Recipe)
        self.ingredient_foods = BaseAccessModel(DEFAULT_PK, IngredientFoodModel, IngredientFood)
        self.ingredient_units = BaseAccessModel(DEFAULT_PK, IngredientUnitModel, IngredientUnit)
        self.comments = BaseAccessModel(DEFAULT_PK, RecipeComment, CommentOut)

        # Tags and Categories
        self.categories = CategoryDataAccessModel("slug", Category, RecipeCategoryResponse)
        self.tags = TagsDataAccessModel("slug", Tag, RecipeTagResponse)

        # Site
        self.settings = BaseAccessModel(DEFAULT_PK, SiteSettings, SiteSettingsSchema)
        self.themes = BaseAccessModel(DEFAULT_PK, SiteThemeModel, SiteTheme)
        self.sign_ups = BaseAccessModel("token", SignUp, SignUpOut)
        self.custom_pages = BaseAccessModel(DEFAULT_PK, CustomPage, CustomPageOut)
        self.event_notifications = BaseAccessModel(DEFAULT_PK, EventNotification, EventNotificationIn)
        self.events = BaseAccessModel(DEFAULT_PK, Event, EventSchema)

        # Users / Groups
        self.users = UserDataAccessModel(DEFAULT_PK, User, UserInDB)
        self.api_tokens = BaseAccessModel(DEFAULT_PK, LongLiveToken, LongLiveTokenInDB)
        self.groups = GroupDataAccessModel(DEFAULT_PK, Group, GroupInDB)
        self.meals = BaseAccessModel("uid", MealPlan, MealPlanOut)
        self.shopping_lists = BaseAccessModel(DEFAULT_PK, ShoppingList, ShoppingListOut)
