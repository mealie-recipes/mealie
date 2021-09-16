from logging import getLogger

from sqlalchemy.orm.session import Session

from mealie.db.data_access_layer.group_access_model import GroupDataAccessModel
from mealie.db.models.event import Event, EventNotification
from mealie.db.models.group import Group
from mealie.db.models.group.cookbook import CookBook
from mealie.db.models.group.invite_tokens import GroupInviteToken
from mealie.db.models.group.preferences import GroupPreferencesModel
from mealie.db.models.group.shopping_list import ShoppingList
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.comment import RecipeComment
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
from mealie.db.models.recipe.recipe import RecipeModel, Tag
from mealie.db.models.settings import SiteSettings
from mealie.db.models.sign_up import SignUp
from mealie.db.models.users import LongLiveToken, User
from mealie.schema.admin import SiteSettings as SiteSettingsSchema
from mealie.schema.cookbook import ReadCookBook
from mealie.schema.events import Event as EventSchema
from mealie.schema.events import EventNotificationIn
from mealie.schema.group.group_preferences import ReadGroupPreferences
from mealie.schema.group.invite_token import ReadInviteToken
from mealie.schema.meal_plan import ShoppingListOut
from mealie.schema.recipe import (
    CommentOut,
    IngredientFood,
    IngredientUnit,
    Recipe,
    RecipeCategoryResponse,
    RecipeTagResponse,
)
from mealie.schema.user import GroupInDB, LongLiveTokenInDB, PrivateUser, SignUpOut

from ._base_access_model import BaseAccessModel
from .recipe_access_model import RecipeDataAccessModel
from .user_access_model import UserDataAccessModel

logger = getLogger()


pk_id = "id"
pk_slug = "slug"
pk_token = "token"


class CategoryDataAccessModel(BaseAccessModel):
    def get_empty(self, session: Session):
        return session.query(Category).filter(~Category.recipes.any()).all()


class TagsDataAccessModel(BaseAccessModel):
    def get_empty(self, session: Session):
        return session.query(Tag).filter(~Tag.recipes.any()).all()


class DatabaseAccessLayer:
    def __init__(self) -> None:
        """
        `DatabaseAccessLayer` class is the data access layer for all database actions within
        Mealie. Database uses composition from classes derived from BaseAccessModel. These
        can be substantiated from the BaseAccessModel class or through inheritance when
        additional methods are required.
        """

        # Recipes
        self.recipes = RecipeDataAccessModel(pk_slug, RecipeModel, Recipe)
        self.ingredient_foods = BaseAccessModel(pk_id, IngredientFoodModel, IngredientFood)
        self.ingredient_units = BaseAccessModel(pk_id, IngredientUnitModel, IngredientUnit)
        self.comments = BaseAccessModel(pk_id, RecipeComment, CommentOut)

        # Tags and Categories
        self.categories = CategoryDataAccessModel(pk_slug, Category, RecipeCategoryResponse)
        self.tags = TagsDataAccessModel(pk_slug, Tag, RecipeTagResponse)

        # Site
        self.settings = BaseAccessModel(pk_id, SiteSettings, SiteSettingsSchema)
        self.sign_ups = BaseAccessModel(pk_token, SignUp, SignUpOut)
        self.event_notifications = BaseAccessModel(pk_id, EventNotification, EventNotificationIn)
        self.events = BaseAccessModel(pk_id, Event, EventSchema)

        # Users
        self.users = UserDataAccessModel(pk_id, User, PrivateUser)
        self.api_tokens = BaseAccessModel(pk_id, LongLiveToken, LongLiveTokenInDB)

        # Group Data
        self.groups = GroupDataAccessModel(pk_id, Group, GroupInDB)
        self.group_tokens = BaseAccessModel("token", GroupInviteToken, ReadInviteToken)
        self.shopping_lists = BaseAccessModel(pk_id, ShoppingList, ShoppingListOut)
        self.cookbooks = BaseAccessModel(pk_id, CookBook, ReadCookBook)
        self.group_preferences = BaseAccessModel("group_id", GroupPreferencesModel, ReadGroupPreferences)
