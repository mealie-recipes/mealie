from collections.abc import Sequence
from functools import cached_property

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm import Session

from mealie.db.models.group import Group, ReportEntryModel, ReportModel
from mealie.db.models.group.exports import GroupDataExportsModel
from mealie.db.models.group.preferences import GroupPreferencesModel
from mealie.db.models.household.cookbook import CookBook
from mealie.db.models.household.events import GroupEventNotifierModel
from mealie.db.models.household.household import Household
from mealie.db.models.household.household_to_recipe import HouseholdToRecipe
from mealie.db.models.household.invite_tokens import GroupInviteToken
from mealie.db.models.household.mealplan import GroupMealPlan, GroupMealPlanRules
from mealie.db.models.household.preferences import HouseholdPreferencesModel
from mealie.db.models.household.recipe_action import GroupRecipeAction
from mealie.db.models.household.shopping_list import (
    ShoppingList,
    ShoppingListItem,
    ShoppingListItemRecipeReference,
    ShoppingListMultiPurposeLabel,
    ShoppingListRecipeReference,
)
from mealie.db.models.household.webhooks import GroupWebhooksModel
from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.comment import RecipeComment
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.recipe_timeline import RecipeTimelineEvent
from mealie.db.models.recipe.shared import RecipeShareTokenModel
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool
from mealie.db.models.users import LongLiveToken, User
from mealie.db.models.users.password_reset import PasswordResetModel
from mealie.db.models.users.user_to_recipe import UserToRecipe
from mealie.repos.repository_cookbooks import RepositoryCookbooks
from mealie.repos.repository_foods import RepositoryFood
from mealie.repos.repository_household import RepositoryHousehold, RepositoryHouseholdRecipes
from mealie.repos.repository_meal_plan_rules import RepositoryMealPlanRules
from mealie.repos.repository_units import RepositoryUnit
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.group.group_preferences import ReadGroupPreferences
from mealie.schema.household.group_events import GroupEventNotifierOut
from mealie.schema.household.group_recipe_action import GroupRecipeActionOut
from mealie.schema.household.group_shopping_list import (
    ShoppingListItemOut,
    ShoppingListItemRecipeRefOut,
    ShoppingListMultiPurposeLabelOut,
    ShoppingListOut,
    ShoppingListRecipeRefOut,
)
from mealie.schema.household.household import HouseholdInDB, HouseholdRecipeOut
from mealie.schema.household.household_preferences import ReadHouseholdPreferences
from mealie.schema.household.invite_token import ReadInviteToken
from mealie.schema.household.webhook import ReadWebhook
from mealie.schema.labels import MultiPurposeLabelOut
from mealie.schema.meal_plan.new_meal import ReadPlanEntry
from mealie.schema.meal_plan.plan_rules import PlanRulesOut
from mealie.schema.recipe import Recipe, RecipeCommentOut, RecipeToolOut
from mealie.schema.recipe.recipe_category import CategoryOut, TagOut
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit
from mealie.schema.recipe.recipe_share_token import RecipeShareToken
from mealie.schema.recipe.recipe_timeline_events import RecipeTimelineEventOut
from mealie.schema.reports.reports import ReportEntryOut, ReportOut
from mealie.schema.user import GroupInDB, LongLiveTokenInDB, PrivateUser
from mealie.schema.user.user import UserRatingOut
from mealie.schema.user.user_passwords import PrivatePasswordResetToken

from ._utils import NOT_SET, NotSet
from .repository_generic import GroupRepositoryGeneric, HouseholdRepositoryGeneric
from .repository_group import RepositoryGroup
from .repository_meals import RepositoryMeals
from .repository_recipes import RepositoryRecipes
from .repository_shopping_list import RepositoryShoppingList
from .repository_users import RepositoryUserRatings, RepositoryUsers

PK_ID = "id"
PK_SLUG = "slug"
PK_TOKEN = "token"
PK_GROUP_ID = "group_id"
PK_HOUSEHOLD_ID = "household_id"


class RepositoryCategories(GroupRepositoryGeneric[CategoryOut, Category]):
    def get_empty(self) -> Sequence[Category]:
        stmt = select(Category).filter(~Category.recipes.any())

        return self.session.execute(stmt).scalars().all()


class RepositoryTags(GroupRepositoryGeneric[TagOut, Tag]):
    def get_empty(self) -> Sequence[Tag]:
        stmt = select(Tag).filter(~Tag.recipes.any())
        return self.session.execute(stmt).scalars().all()


class AllRepositories:
    """
    `AllRepositories` class is the data access layer for all database actions within
    Mealie. Database uses composition from classes derived from AccessModel. These
    can be substantiated from the AccessModel class or through inheritance when
    additional methods are required.
    """

    def __init__(
        self,
        session: Session,
        *,
        group_id: UUID4 | None | NotSet = NOT_SET,
        household_id: UUID4 | None | NotSet = NOT_SET,
    ) -> None:
        self.session = session
        self.group_id = group_id
        self.household_id = household_id

    # ================================================================
    # Recipe

    @cached_property
    def recipes(self) -> RepositoryRecipes:
        return RepositoryRecipes(
            self.session, PK_SLUG, RecipeModel, Recipe, group_id=self.group_id, household_id=self.household_id
        )

    @cached_property
    def ingredient_foods(self) -> RepositoryFood:
        return RepositoryFood(self.session, PK_ID, IngredientFoodModel, IngredientFood, group_id=self.group_id)

    @cached_property
    def ingredient_units(self) -> RepositoryUnit:
        return RepositoryUnit(self.session, PK_ID, IngredientUnitModel, IngredientUnit, group_id=self.group_id)

    @cached_property
    def tools(self) -> GroupRepositoryGeneric[RecipeToolOut, Tool]:
        return GroupRepositoryGeneric(self.session, PK_ID, Tool, RecipeToolOut, group_id=self.group_id)

    @cached_property
    def comments(self) -> GroupRepositoryGeneric[RecipeCommentOut, RecipeComment]:
        # Since users can comment on recipes that belong to other households,
        # this is a group repository, rather than a household repository.
        return GroupRepositoryGeneric(self.session, PK_ID, RecipeComment, RecipeCommentOut, group_id=self.group_id)

    @cached_property
    def categories(self) -> RepositoryCategories:
        return RepositoryCategories(self.session, PK_ID, Category, CategoryOut, group_id=self.group_id)

    @cached_property
    def tags(self) -> RepositoryTags:
        return RepositoryTags(self.session, PK_ID, Tag, TagOut, group_id=self.group_id)

    @cached_property
    def recipe_share_tokens(self) -> GroupRepositoryGeneric[RecipeShareToken, RecipeShareTokenModel]:
        return GroupRepositoryGeneric(
            self.session, PK_ID, RecipeShareTokenModel, RecipeShareToken, group_id=self.group_id
        )

    @cached_property
    def recipe_timeline_events(self) -> GroupRepositoryGeneric[RecipeTimelineEventOut, RecipeTimelineEvent]:
        # Since users can post events on recipes that belong to other households,
        # this is a group repository, rather than a household repository.
        return GroupRepositoryGeneric(
            self.session, PK_ID, RecipeTimelineEvent, RecipeTimelineEventOut, group_id=self.group_id
        )

    # ================================================================
    # User

    @cached_property
    def users(self) -> RepositoryUsers:
        return RepositoryUsers(self.session, PK_ID, User, PrivateUser, group_id=self.group_id)

    @cached_property
    def user_ratings(self) -> RepositoryUserRatings:
        return RepositoryUserRatings(self.session, PK_ID, UserToRecipe, UserRatingOut, group_id=self.group_id)

    @cached_property
    def api_tokens(self) -> GroupRepositoryGeneric[LongLiveTokenInDB, LongLiveToken]:
        return GroupRepositoryGeneric(self.session, PK_ID, LongLiveToken, LongLiveTokenInDB, group_id=self.group_id)

    @cached_property
    def tokens_pw_reset(self) -> GroupRepositoryGeneric[PrivatePasswordResetToken, PasswordResetModel]:
        return GroupRepositoryGeneric(
            self.session, PK_TOKEN, PasswordResetModel, PrivatePasswordResetToken, group_id=self.group_id
        )

    # ================================================================
    # Group

    @cached_property
    def groups(self) -> RepositoryGroup:
        return RepositoryGroup(self.session, PK_ID, Group, GroupInDB)

    @cached_property
    def group_preferences(self) -> GroupRepositoryGeneric[ReadGroupPreferences, GroupPreferencesModel]:
        return GroupRepositoryGeneric(
            self.session, PK_GROUP_ID, GroupPreferencesModel, ReadGroupPreferences, group_id=self.group_id
        )

    @cached_property
    def group_exports(self) -> GroupRepositoryGeneric[GroupDataExport, GroupDataExportsModel]:
        return GroupRepositoryGeneric(
            self.session, PK_ID, GroupDataExportsModel, GroupDataExport, group_id=self.group_id
        )

    @cached_property
    def group_reports(self) -> GroupRepositoryGeneric[ReportOut, ReportModel]:
        return GroupRepositoryGeneric(self.session, PK_ID, ReportModel, ReportOut, group_id=self.group_id)

    @cached_property
    def group_report_entries(self) -> GroupRepositoryGeneric[ReportEntryOut, ReportEntryModel]:
        return GroupRepositoryGeneric(self.session, PK_ID, ReportEntryModel, ReportEntryOut, group_id=self.group_id)

    # ================================================================
    # Household

    @cached_property
    def households(self) -> RepositoryHousehold:
        return RepositoryHousehold(self.session, PK_ID, Household, HouseholdInDB, group_id=self.group_id)

    @cached_property
    def household_preferences(self) -> HouseholdRepositoryGeneric[ReadHouseholdPreferences, HouseholdPreferencesModel]:
        return HouseholdRepositoryGeneric(
            self.session,
            PK_HOUSEHOLD_ID,
            HouseholdPreferencesModel,
            ReadHouseholdPreferences,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    @cached_property
    def household_recipes(self) -> RepositoryHouseholdRecipes:
        return RepositoryHouseholdRecipes(
            self.session,
            PK_ID,
            HouseholdToRecipe,
            HouseholdRecipeOut,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    @cached_property
    def cookbooks(self) -> RepositoryCookbooks:
        return RepositoryCookbooks(
            self.session, PK_ID, CookBook, ReadCookBook, group_id=self.group_id, household_id=self.household_id
        )

    @cached_property
    def group_invite_tokens(self) -> HouseholdRepositoryGeneric[ReadInviteToken, GroupInviteToken]:
        return HouseholdRepositoryGeneric(
            self.session,
            PK_TOKEN,
            GroupInviteToken,
            ReadInviteToken,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    @cached_property
    def group_recipe_actions(self) -> HouseholdRepositoryGeneric[GroupRecipeActionOut, GroupRecipeAction]:
        return HouseholdRepositoryGeneric(
            self.session,
            PK_ID,
            GroupRecipeAction,
            GroupRecipeActionOut,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    # ================================================================
    # Meal Plan

    @cached_property
    def meals(self) -> RepositoryMeals:
        return RepositoryMeals(
            self.session, PK_ID, GroupMealPlan, ReadPlanEntry, group_id=self.group_id, household_id=self.household_id
        )

    @cached_property
    def group_meal_plan_rules(self) -> RepositoryMealPlanRules:
        return RepositoryMealPlanRules(
            self.session,
            PK_ID,
            GroupMealPlanRules,
            PlanRulesOut,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    # ================================================================
    # Shopping List

    @cached_property
    def group_shopping_lists(self) -> RepositoryShoppingList:
        return RepositoryShoppingList(
            self.session, PK_ID, ShoppingList, ShoppingListOut, group_id=self.group_id, household_id=self.household_id
        )

    @cached_property
    def group_shopping_list_item(self) -> HouseholdRepositoryGeneric[ShoppingListItemOut, ShoppingListItem]:
        return HouseholdRepositoryGeneric(
            self.session,
            PK_ID,
            ShoppingListItem,
            ShoppingListItemOut,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    @cached_property
    def group_shopping_list_item_references(
        self,
    ) -> HouseholdRepositoryGeneric[ShoppingListItemRecipeRefOut, ShoppingListItemRecipeReference]:
        return HouseholdRepositoryGeneric(
            self.session,
            PK_ID,
            ShoppingListItemRecipeReference,
            ShoppingListItemRecipeRefOut,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    @cached_property
    def group_shopping_list_recipe_refs(
        self,
    ) -> HouseholdRepositoryGeneric[ShoppingListRecipeRefOut, ShoppingListRecipeReference]:
        return HouseholdRepositoryGeneric(
            self.session,
            PK_ID,
            ShoppingListRecipeReference,
            ShoppingListRecipeRefOut,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    @cached_property
    def shopping_list_multi_purpose_labels(
        self,
    ) -> HouseholdRepositoryGeneric[ShoppingListMultiPurposeLabelOut, ShoppingListMultiPurposeLabel]:
        return HouseholdRepositoryGeneric(
            self.session,
            PK_ID,
            ShoppingListMultiPurposeLabel,
            ShoppingListMultiPurposeLabelOut,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    @cached_property
    def group_multi_purpose_labels(self) -> GroupRepositoryGeneric[MultiPurposeLabelOut, MultiPurposeLabel]:
        return GroupRepositoryGeneric(
            self.session, PK_ID, MultiPurposeLabel, MultiPurposeLabelOut, group_id=self.group_id
        )

    # ================================================================
    # Events

    @cached_property
    def group_event_notifier(self) -> HouseholdRepositoryGeneric[GroupEventNotifierOut, GroupEventNotifierModel]:
        return HouseholdRepositoryGeneric(
            self.session,
            PK_ID,
            GroupEventNotifierModel,
            GroupEventNotifierOut,
            group_id=self.group_id,
            household_id=self.household_id,
        )

    @cached_property
    def webhooks(self) -> HouseholdRepositoryGeneric[ReadWebhook, GroupWebhooksModel]:
        return HouseholdRepositoryGeneric(
            self.session, PK_ID, GroupWebhooksModel, ReadWebhook, group_id=self.group_id, household_id=self.household_id
        )
