from datetime import date
from functools import cached_property

from dateutil.tz import tzlocal
from fastapi import APIRouter, Depends, HTTPException

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_meals import RepositoryMeals
from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BaseCrudController
from mealie.routes._base.mixins import HttpRepo
from mealie.schema import mapper
from mealie.schema.meal_plan import CreatePlanEntry, ReadPlanEntry, SavePlanEntry, UpdatePlanEntry
from mealie.schema.meal_plan.new_meal import CreateRandomEntry, PlanEntryPagination, PlanEntryType
from mealie.schema.meal_plan.plan_rules import PlanRulesDay
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import ErrorResponse
from mealie.services.event_bus_service.event_types import EventMealplanCreatedData, EventTypes

router = APIRouter(prefix="/households/mealplans", tags=["Households: Mealplans"])


@controller(router)
class GroupMealplanController(BaseCrudController):
    @cached_property
    def repo(self) -> RepositoryMeals:
        return self.repos.meals

    def registered_exceptions(self, ex: type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.translator),
        }
        return registered.get(ex, self.t("generic.server-error"))

    @cached_property
    def mixins(self):
        return HttpRepo[CreatePlanEntry, ReadPlanEntry, UpdatePlanEntry](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    def _get_random_recipes_from_mealplan(
        self, plan_date: date, entry_type: PlanEntryType, limit: int = 1
    ) -> list[Recipe]:
        """
        Gets rules for a mealplan and returns a list of random recipes based on the rules.
        May return zero recipes if no recipes match the filter criteria.

        Recipes from all households are included unless the rules specify a household filter.
        """

        rules = self.repos.group_meal_plan_rules.get_rules(PlanRulesDay.from_date(plan_date), entry_type.value)
        cross_household_recipes = get_repositories(self.session, group_id=self.group_id, household_id=None).recipes

        qf_string = " AND ".join([f"({rule.query_filter_string})" for rule in rules if rule.query_filter_string])
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
    ):
        # merge start and end dates into pagination query only if either is provided
        if start_date or end_date:
            if not start_date:
                date_filter = f"date <= {end_date}"

            elif not end_date:
                date_filter = f"date >= {start_date}"

            else:
                date_filter = f"date >= {start_date} AND date <= {end_date}"

            if q.query_filter:
                q.query_filter = f"({q.query_filter}) AND ({date_filter})"

            else:
                q.query_filter = date_filter

        return self.repo.page_all(pagination=q)

    @router.post("", response_model=ReadPlanEntry, status_code=201)
    def create_one(self, data: CreatePlanEntry):
        data = mapper.cast(data, SavePlanEntry, group_id=self.group_id, user_id=self.user.id)
        result = self.mixins.create_one(data)

        self.publish_event(
            event_type=EventTypes.mealplan_entry_created,
            document_data=EventMealplanCreatedData(
                mealplan_id=result.id,
                recipe_id=data.recipe_id,
                recipe_name=result.recipe.name if result.recipe else None,
                recipe_slug=result.recipe.slug if result.recipe else None,
                date=data.date,
            ),
            group_id=result.group_id,
            household_id=result.household_id,
            message=f"Mealplan entry created for {data.date} for {data.entry_type}",
        )

        return result

    @router.get("/today")
    def get_todays_meals(self):
        local_tz = tzlocal()
        return self.repo.get_today(tz=local_tz)

    @router.post("/random", response_model=ReadPlanEntry)
    def create_random_meal(self, data: CreateRandomEntry):
        """
        `create_random_meal` is a route that provides the randomized functionality for mealplaners.
        It operates by following the rules set out in the household's mealplan settings. If no settings
        are set, it will return any random meal.

        Refer to the mealplan settings routes for more information on how rules can be applied
        to the random meal selector.
        """
        random_recipes = self._get_random_recipes_from_mealplan(data.date, data.entry_type)
        if not random_recipes:
            raise HTTPException(
                status_code=404, detail=ErrorResponse.respond(message=self.t("mealplan.no-recipes-match-your-rules"))
            )

        recipe = random_recipes[0]
        return self.mixins.create_one(
            SavePlanEntry(
                date=data.date,
                entry_type=data.entry_type,
                recipe_id=recipe.id,
                group_id=self.group_id,
                user_id=self.user.id,
            )
        )

    @router.get("/{item_id}", response_model=ReadPlanEntry)
    def get_one(self, item_id: int):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=ReadPlanEntry)
    def update_one(self, item_id: int, data: UpdatePlanEntry):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=ReadPlanEntry)
    def delete_one(self, item_id: int):
        return self.mixins.delete_one(item_id)
