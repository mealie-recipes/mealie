from functools import cached_property

from sqlalchemy.orm import Session

from mealie.db.models.event import Event, EventNotification
from mealie.db.models.group import Group, GroupMealPlan
from mealie.db.models.group.cookbook import CookBook
from mealie.db.models.group.invite_tokens import GroupInviteToken
from mealie.db.models.group.preferences import GroupPreferencesModel
from mealie.db.models.group.webhooks import GroupWebhooksModel
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.comment import RecipeComment
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.settings import SiteSettings
from mealie.db.models.sign_up import SignUp
from mealie.db.models.users import LongLiveToken, User
from mealie.schema.admin import SiteSettings as SiteSettingsSchema
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.events import Event as EventSchema
from mealie.schema.events import EventNotificationIn
from mealie.schema.group.group_preferences import ReadGroupPreferences
from mealie.schema.group.invite_token import ReadInviteToken
from mealie.schema.group.webhook import ReadWebhook
from mealie.schema.meal_plan.new_meal import ReadPlanEntry
from mealie.schema.recipe import CommentOut, Recipe, RecipeCategoryResponse, RecipeTagResponse
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit
from mealie.schema.user import GroupInDB, LongLiveTokenInDB, PrivateUser, SignUpOut

from ._access_model import AccessModel
from .group_access_model import GroupDataAccessModel
from .meal_access_model import MealDataAccessModel
from .recipe_access_model import RecipeDataAccessModel
from .user_access_model import UserDataAccessModel

pk_id = "id"
pk_slug = "slug"
pk_token = "token"


class CategoryDataAccessModel(AccessModel):
    def get_empty(self):
        return self.session.query(Category).filter(~Category.recipes.any()).all()


class TagsDataAccessModel(AccessModel):
    def get_empty(self):
        return self.session.query(Tag).filter(~Tag.recipes.any()).all()


class Database:
    def __init__(self, session: Session) -> None:
        """
        `DatabaseAccessLayer` class is the data access layer for all database actions within
        Mealie. Database uses composition from classes derived from BaseAccessModel. These
        can be substantiated from the BaseAccessModel class or through inheritance when
        additional methods are required.
        """

        self.session = session

    # ================================================================
    # Recipe Items

    @cached_property
    def recipes(self) -> RecipeDataAccessModel:
        return RecipeDataAccessModel(self.session, pk_slug, RecipeModel, Recipe)

    @cached_property
    def ingredient_foods(self) -> AccessModel:
        return AccessModel(self.session, pk_id, IngredientFoodModel, IngredientFood)

    @cached_property
    def ingredient_units(self) -> AccessModel:
        return AccessModel(self.session, pk_id, IngredientUnitModel, IngredientUnit)

    @cached_property
    def comments(self) -> AccessModel:
        return AccessModel(self.session, pk_id, RecipeComment, CommentOut)

    @cached_property
    def categories(self) -> CategoryDataAccessModel:
        return CategoryDataAccessModel(self.session, pk_id, Category, RecipeCategoryResponse)

    @cached_property
    def tags(self) -> TagsDataAccessModel:
        return TagsDataAccessModel(self.session, pk_id, Tag, RecipeTagResponse)

    # ================================================================
    # Site Items

    @cached_property
    def settings(self) -> AccessModel:
        return AccessModel(self.session, pk_id, SiteSettings, SiteSettingsSchema)

    @cached_property
    def sign_up(self) -> AccessModel:
        return AccessModel(self.session, pk_id, SignUp, SignUpOut)

    @cached_property
    def event_notifications(self) -> AccessModel:
        return AccessModel(self.session, pk_id, EventNotification, EventNotificationIn)

    @cached_property
    def events(self) -> AccessModel:
        return AccessModel(self.session, pk_id, Event, EventSchema)

    # ================================================================
    # User Items

    @cached_property
    def users(self) -> UserDataAccessModel:
        return UserDataAccessModel(self.session, pk_id, User, PrivateUser)

    @cached_property
    def api_tokens(self) -> AccessModel:
        return AccessModel(self.session, pk_id, LongLiveToken, LongLiveTokenInDB)

    # ================================================================
    # Group Items

    @cached_property
    def groups(self) -> GroupDataAccessModel:
        return GroupDataAccessModel(self.session, pk_id, Group, GroupInDB)

    @cached_property
    def group_invite_tokens(self) -> AccessModel:
        return AccessModel(self.session, "token", GroupInviteToken, ReadInviteToken)

    @cached_property
    def group_preferences(self) -> AccessModel:
        return AccessModel(self.session, "group_id", GroupPreferencesModel, ReadGroupPreferences)

    @cached_property
    def meals(self) -> MealDataAccessModel:
        return MealDataAccessModel(self.session, pk_id, GroupMealPlan, ReadPlanEntry)

    @cached_property
    def cookbooks(self) -> AccessModel:
        return AccessModel(self.session, pk_id, CookBook, ReadCookBook)

    @cached_property
    def webhooks(self) -> AccessModel:
        return AccessModel(self.session, pk_id, GroupWebhooksModel, ReadWebhook)
