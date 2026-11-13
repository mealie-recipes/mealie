from datetime import date
from functools import cached_property
from uuid import UUID

from dateutil.tz import tzlocal
from fastapi import APIRouter, Depends

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_meals import RepositoryMeals
from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BaseCrudController
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.permissions import not_found
from mealie.schema import mapper
from mealie.schema.meal_plan import PlanEntryCreate, PlanEntryOut, PlanEntrySave, PlanEntryUpdate
from mealie.schema.meal_plan.new_meal import PlanEntryPagination, PlanEntryType, RandomPlanEntryCreate
from mealie.schema.meal_plan.plan_rules import PlanRulesDay
from mealie.schema.recipe.recipe import RecipeOut
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.event_bus_service.event_types import (
    EventMealplanData,
    EventOperation,
    EventTypes,
)
from mealie.services.query_filter.builder import QueryFilterBuilder

router = APIRouter(prefix="/households/mealplans", tags=["Households: Meal Plans"])

MEALPLAN_NOTIFICATION_KEYS: dict[EventOperation, tuple[str, str]] = {
    EventOperation.create: ("notifications.mealplan-entry-created", "notifications.mealplan-range-entry-created"),
    EventOperation.update: ("notifications.mealplan-entry-updated", "notifications.mealplan-range-entry-updated"),
    EventOperation.delete: ("notifications.mealplan-entry-deleted", "notifications.mealplan-range-entry-deleted"),
}
"""Notification message translation keys per operation, as `(day entry key, date range entry key)`"""


@controller(router)
class GroupMealplanController(BaseCrudController):
    @cached_property
    def repo(self) -> RepositoryMeals:
        return self.repos.meals

    @cached_property
    def group_recipes(self):
        # Entries may reference recipes from any household in the group, so the household-scoped repo is too narrow.
        return get_repositories(self.session, group_id=self.group_id, household_id=None).recipes

    def _require_group_recipe(self, recipe_id: UUID | None) -> None:
        if recipe_id is not None and self.group_recipes.get_one(recipe_id, "id") is None:
            raise not_found()

    def _translated_entry_type(self, entry_type) -> str:
        value = getattr(entry_type, "value", entry_type)
        return self.t(f"mealplan.entry-type.{value}", default=str(value))

    def _notification_message(self, operation: EventOperation, entry: PlanEntryOut) -> str:
        day_key, range_key = MEALPLAN_NOTIFICATION_KEYS[operation]
        return self.t(
            range_key if entry.end_date else day_key,
            date=entry.date,
            end_date=entry.end_date,
            entry_type=self._translated_entry_type(entry.entry_type),
        )

    def registered_exceptions(self, ex: type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.translator),
        }
        return registered.get(ex, self.t("generic.server-error"))

    @cached_property
    def mixins(self):
        return HttpRepo[PlanEntryCreate, PlanEntryOut, PlanEntryUpdate](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    def _get_random_recipes_from_mealplan(
        self, plan_date: date, entry_type: PlanEntryType, limit: int = 1, end_date: date | None = None
    ) -> list[RecipeOut]:
        """
        Gets rules for a mealplan and returns a list of random recipes based on the rules.
        May return zero recipes if no recipes match the filter criteria.

        Recipes from all households are included unless the rules specify a household filter.
        """

        # date range entries (e.g. a week) aren't on a specific weekday, so only rules for all days apply to them
        day = PlanRulesDay.unset if end_date else PlanRulesDay.from_date(plan_date)
        rules = self.repos.group_meal_plan_rules.get_rules(day, entry_type.value)
        cross_household_recipes = get_repositories(
            self.session, group_id=self.group_id, household_id=None
        ).recipes.by_user(self.user.id)

        qf_string = QueryFilterBuilder.combine_filters(*[rule.query_filter_string for rule in rules])
        recipes_data = cross_household_recipes.page_all(
            pagination=PaginationQuery(
                page=1,
                per_page=limit,
                query_filter=qf_string,
                order_by="random",
                pagination_seed=self.repo._random_seed(),
            )
        )
        return recipes_data.items

    @router.get("", response_model=PlanEntryPagination)
    def get_all(
        self,
        q: PaginationQuery = Depends(PaginationQuery),
        start_date: date | None = None,
        end_date: date | None = None,
        include_week_entries: bool = False,
    ):
        # week entries are opt-in so existing API clients, which expect every entry to be on a specific day,
        # aren't handed them
        week_filter = None if include_week_entries else "end_date IS NULL"

        # merge start and end dates into pagination query only if either is provided
        date_filters: list[str] = []
        if start_date:
            # a week entry starting before `start_date` still overlaps the range if it ends on or after it
            date_filters.append(f"(date >= {start_date} OR end_date >= {start_date})")
        if end_date:
            date_filters.append(f"date <= {end_date}")

        q.query_filter = QueryFilterBuilder.combine_filters(q.query_filter, week_filter, *date_filters)

        return self.repo.page_all(pagination=q)

    @router.post("", response_model=PlanEntryOut, status_code=201)
    def create_one(self, data: PlanEntryCreate):
        self._require_group_recipe(data.recipe_id)
        data = mapper.cast(data, PlanEntrySave, group_id=self.group_id, user_id=self.user.id)
        result = self.mixins.create_one(data)

        self.publish_event(
            event_type=EventTypes.mealplan_entry_created,
            document_data=EventMealplanData(
                operation=EventOperation.create,
                mealplan_id=result.id,
                recipe_id=data.recipe_id,
                recipe_name=result.recipe.name if result.recipe else None,
                recipe_slug=result.recipe.slug if result.recipe else None,
                date=data.date,
                end_date=data.end_date,
            ),
            group_id=result.group_id,
            household_id=result.household_id,
            message=self._notification_message(EventOperation.create, result),
        )

        return result

    @router.get("/today")
    def get_todays_meals(self):
        local_tz = tzlocal()
        return self.repo.get_today(tz=local_tz)

    @router.post("/random", response_model=PlanEntryOut)
    def create_random_meal(self, data: RandomPlanEntryCreate):
        """
        `create_random_meal` is a route that provides the randomized functionality for meal planners.
        It operates by following the rules set out in the household's meal plan settings. If no settings
        are set, it will return any random meal.

        Refer to the meal plan settings routes for more information on how rules can be applied
        to the random meal selector.
        """
        random_recipes = self._get_random_recipes_from_mealplan(data.date, data.entry_type, end_date=data.end_date)
        if not random_recipes:
            raise not_found(self.t("mealplan.no-recipes-match-your-rules"))

        recipe = random_recipes[0]
        result = self.mixins.create_one(
            PlanEntrySave(
                date=data.date,
                end_date=data.end_date,
                entry_type=data.entry_type,
                recipe_id=recipe.id,
                group_id=self.group_id,
                user_id=self.user.id,
            )
        )

        self.publish_event(
            event_type=EventTypes.mealplan_entry_created,
            document_data=EventMealplanData(
                operation=EventOperation.create,
                mealplan_id=result.id,
                recipe_id=recipe.id,
                recipe_name=recipe.name,
                recipe_slug=recipe.slug,
                date=data.date,
                end_date=data.end_date,
            ),
            group_id=result.group_id,
            household_id=result.household_id,
            message=self._notification_message(EventOperation.create, result),
        )

        return result

    @router.get("/{item_id}", response_model=PlanEntryOut)
    def get_one(self, item_id: int):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=PlanEntryOut)
    def update_one(self, item_id: int, data: PlanEntryUpdate):
        self._require_group_recipe(data.recipe_id)
        result = self.mixins.update_one(data, item_id)

        self.publish_event(
            event_type=EventTypes.mealplan_entry_updated,
            document_data=EventMealplanData(
                operation=EventOperation.update,
                mealplan_id=result.id,
                recipe_id=result.recipe_id,
                recipe_name=result.recipe.name if result.recipe else None,
                recipe_slug=result.recipe.slug if result.recipe else None,
                date=result.date,
                end_date=result.end_date,
            ),
            group_id=result.group_id,
            household_id=result.household_id,
            message=self._notification_message(EventOperation.update, result),
        )

        return result

    @router.delete("/{item_id}", response_model=PlanEntryOut)
    def delete_one(self, item_id: int):
        result = self.mixins.delete_one(item_id)

        self.publish_event(
            event_type=EventTypes.mealplan_entry_deleted,
            document_data=EventMealplanData(
                operation=EventOperation.delete,
                mealplan_id=result.id,
                recipe_id=result.recipe_id,
                recipe_name=result.recipe.name if result.recipe else None,
                recipe_slug=result.recipe.slug if result.recipe else None,
                date=result.date,
                end_date=result.end_date,
            ),
            group_id=result.group_id,
            household_id=result.household_id,
            message=self._notification_message(EventOperation.delete, result),
        )

        return result
