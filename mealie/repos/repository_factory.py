from functools import cached_property

from sqlalchemy.orm import Session

from mealie.db.models.event import Event, EventNotification
from mealie.db.models.group import Group, GroupMealPlan, ReportEntryModel, ReportModel
from mealie.db.models.group.cookbook import CookBook
from mealie.db.models.group.exports import GroupDataExportsModel
from mealie.db.models.group.invite_tokens import GroupInviteToken
from mealie.db.models.group.preferences import GroupPreferencesModel
from mealie.db.models.group.shopping_list import ShoppingList, ShoppingListItem
from mealie.db.models.group.webhooks import GroupWebhooksModel
from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.comment import RecipeComment
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.shared import RecipeShareTokenModel
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool
from mealie.db.models.server.task import ServerTaskModel
from mealie.db.models.sign_up import SignUp
from mealie.db.models.users import LongLiveToken, User
from mealie.db.models.users.password_reset import PasswordResetModel
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.events import Event as EventSchema
from mealie.schema.events import EventNotificationIn
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.group.group_preferences import ReadGroupPreferences
from mealie.schema.group.group_shopping_list import ShoppingListItemOut, ShoppingListOut
from mealie.schema.group.invite_token import ReadInviteToken
from mealie.schema.group.webhook import ReadWebhook
from mealie.schema.labels import MultiPurposeLabelOut
from mealie.schema.meal_plan.new_meal import ReadPlanEntry
from mealie.schema.recipe import Recipe, RecipeCategoryResponse, RecipeCommentOut, RecipeTagResponse, RecipeTool
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit
from mealie.schema.recipe.recipe_share_token import RecipeShareToken
from mealie.schema.reports.reports import ReportEntryOut, ReportOut
from mealie.schema.server import ServerTask
from mealie.schema.user import GroupInDB, LongLiveTokenInDB, PrivateUser, SignUpOut
from mealie.schema.user.user_passwords import PrivatePasswordResetToken

from .repository_generic import RepositoryGeneric
from .repository_group import RepositoryGroup
from .repository_meals import RepositoryMeals
from .repository_recipes import RepositoryRecipes
from .repository_shopping_list import RepositoryShoppingList
from .repository_users import RepositoryUsers

pk_id = "id"
pk_slug = "slug"
pk_token = "token"
pk_group_id = "group_id"


class RepositoryCategories(RepositoryGeneric):
    def get_empty(self):
        return self.session.query(Category).filter(~Category.recipes.any()).all()


class RepositoryTags(RepositoryGeneric):
    def get_empty(self):
        return self.session.query(Tag).filter(~Tag.recipes.any()).all()


class AllRepositories:
    def __init__(self, session: Session) -> None:
        """
        `AllRepositories` class is the data access layer for all database actions within
        Mealie. Database uses composition from classes derived from AccessModel. These
        can be substantiated from the AccessModel class or through inheritance when
        additional methods are required.
        """

        self.session = session

    # ================================================================
    # Recipe Items

    @cached_property
    def recipes(self) -> RepositoryRecipes:
        return RepositoryRecipes(self.session, pk_slug, RecipeModel, Recipe)

    @cached_property
    def ingredient_foods(self) -> RepositoryGeneric[IngredientFood, IngredientFoodModel]:
        return RepositoryGeneric(self.session, pk_id, IngredientFoodModel, IngredientFood)

    @cached_property
    def ingredient_units(self) -> RepositoryGeneric[IngredientUnit, IngredientUnitModel]:
        return RepositoryGeneric(self.session, pk_id, IngredientUnitModel, IngredientUnit)

    @cached_property
    def tools(self) -> RepositoryGeneric[RecipeTool, Tool]:
        return RepositoryGeneric(self.session, pk_id, Tool, RecipeTool)

    @cached_property
    def comments(self) -> RepositoryGeneric[RecipeCommentOut, RecipeComment]:
        return RepositoryGeneric(self.session, pk_id, RecipeComment, RecipeCommentOut)

    @cached_property
    def categories(self) -> RepositoryCategories:
        return RepositoryCategories(self.session, pk_slug, Category, RecipeCategoryResponse)

    @cached_property
    def tags(self) -> RepositoryTags:
        return RepositoryTags(self.session, pk_slug, Tag, RecipeTagResponse)

    @cached_property
    def recipe_share_tokens(self) -> RepositoryGeneric[RecipeShareToken, RecipeShareTokenModel]:
        return RepositoryGeneric(self.session, pk_id, RecipeShareTokenModel, RecipeShareToken)

    # ================================================================
    # Site Items

    @cached_property
    def sign_up(self) -> RepositoryGeneric[SignUpOut, SignUp]:
        return RepositoryGeneric(self.session, pk_id, SignUp, SignUpOut)

    @cached_property
    def event_notifications(self) -> RepositoryGeneric[EventNotificationIn, EventNotification]:
        return RepositoryGeneric(self.session, pk_id, EventNotification, EventNotificationIn)

    @cached_property
    def events(self) -> RepositoryGeneric[EventSchema, Event]:
        return RepositoryGeneric(self.session, pk_id, Event, EventSchema)

    # ================================================================
    # User Items

    @cached_property
    def users(self) -> RepositoryUsers:
        return RepositoryUsers(self.session, pk_id, User, PrivateUser)

    @cached_property
    def api_tokens(self) -> RepositoryGeneric[LongLiveTokenInDB, LongLiveToken]:
        return RepositoryGeneric(self.session, pk_id, LongLiveToken, LongLiveTokenInDB)

    @cached_property
    def tokens_pw_reset(self) -> RepositoryGeneric[PrivatePasswordResetToken, PasswordResetModel]:
        return RepositoryGeneric(self.session, pk_token, PasswordResetModel, PrivatePasswordResetToken)

    # ================================================================
    # Group Items

    @cached_property
    def server_tasks(self) -> RepositoryGeneric[ServerTask, ServerTaskModel]:
        return RepositoryGeneric(self.session, pk_id, ServerTaskModel, ServerTask)

    @cached_property
    def groups(self) -> RepositoryGroup:
        return RepositoryGroup(self.session, pk_id, Group, GroupInDB)

    @cached_property
    def group_invite_tokens(self) -> RepositoryGeneric[ReadInviteToken, GroupInviteToken]:
        return RepositoryGeneric(self.session, pk_token, GroupInviteToken, ReadInviteToken)

    @cached_property
    def group_preferences(self) -> RepositoryGeneric[ReadGroupPreferences, GroupPreferencesModel]:
        return RepositoryGeneric(self.session, pk_group_id, GroupPreferencesModel, ReadGroupPreferences)

    @cached_property
    def group_exports(self) -> RepositoryGeneric[GroupDataExport, GroupDataExportsModel]:
        return RepositoryGeneric(self.session, pk_id, GroupDataExportsModel, GroupDataExport)

    @cached_property
    def meals(self) -> RepositoryMeals:
        return RepositoryMeals(self.session, pk_id, GroupMealPlan, ReadPlanEntry)

    @cached_property
    def cookbooks(self) -> RepositoryGeneric[ReadCookBook, CookBook]:
        return RepositoryGeneric(self.session, pk_id, CookBook, ReadCookBook)

    @cached_property
    def webhooks(self) -> RepositoryGeneric[ReadWebhook, GroupWebhooksModel]:
        return RepositoryGeneric(self.session, pk_id, GroupWebhooksModel, ReadWebhook)

    @cached_property
    def group_reports(self) -> RepositoryGeneric[ReportOut, ReportModel]:
        return RepositoryGeneric(self.session, pk_id, ReportModel, ReportOut)

    @cached_property
    def group_report_entries(self) -> RepositoryGeneric[ReportEntryOut, ReportEntryModel]:
        return RepositoryGeneric(self.session, pk_id, ReportEntryModel, ReportEntryOut)

    @cached_property
    def group_shopping_lists(self) -> RepositoryShoppingList:
        return RepositoryShoppingList(self.session, pk_id, ShoppingList, ShoppingListOut)

    @cached_property
    def group_shopping_list_item(self) -> RepositoryGeneric[ShoppingListItemOut, ShoppingListItem]:
        return RepositoryGeneric(self.session, pk_id, ShoppingListItem, ShoppingListItemOut)

    @cached_property
    def group_multi_purpose_labels(self) -> RepositoryGeneric[MultiPurposeLabelOut, MultiPurposeLabel]:
        return RepositoryGeneric(self.session, pk_id, MultiPurposeLabel, MultiPurposeLabelOut)
