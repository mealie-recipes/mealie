from datetime import date, timedelta
from functools import cached_property
from typing import Type

from fastapi import APIRouter

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.repos.repository_meals import RepositoryMeals
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import CrudMixins
from mealie.schema import mapper
from mealie.schema.meal_plan import CreatePlanEntry, ReadPlanEntry, SavePlanEntry, UpdatePlanEntry

router = APIRouter(prefix="/groups/mealplans", tags=["Groups: Mealplans"])


@controller(router)
class GroupMealplanController(BaseUserController):
    @cached_property
    def repo(self) -> RepositoryMeals:
        return self.repos.meals.by_group(self.group_id)

    def registered_exceptions(self, ex: Type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.deps.t),
        }
        return registered.get(ex, "An unexpected error occurred.")

    @cached_property
    def mixins(self):
        return CrudMixins[CreatePlanEntry, ReadPlanEntry, UpdatePlanEntry](
            self.repo,
            self.deps.logger,
            self.registered_exceptions,
        )

    @router.get("/today", tags=["Groups: Mealplans"])
    def get_todays_meals(self):
        return self.repo.get_today(group_id=self.group_id)

    @router.get("", response_model=list[ReadPlanEntry])
    def get_all(self, start: date = None, limit: date = None):
        start = start or date.today() - timedelta(days=999)
        limit = limit or date.today() + timedelta(days=999)
        return self.repo.get_slice(start, limit, group_id=self.group.id)

    @router.post("", response_model=ReadPlanEntry, status_code=201)
    def create_one(self, data: CreatePlanEntry):
        data = mapper.cast(data, SavePlanEntry, group_id=self.group.id)
        return self.mixins.create_one(data)

    @router.get("/{item_id}", response_model=ReadPlanEntry)
    def get_one(self, item_id: int):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=ReadPlanEntry)
    def update_one(self, item_id: int, data: UpdatePlanEntry):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=ReadPlanEntry)
    def delete_one(self, item_id: int):
        return self.mixins.delete_one(item_id)
