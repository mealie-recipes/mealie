from functools import cached_property

from fastapi import Depends
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema import mapper
from mealie.schema.meal_plan.plan_rules import PlanRulesCreate, PlanRulesOut, PlanRulesPagination, PlanRulesSave
from mealie.schema.response.pagination import PaginationQuery

router = UserAPIRouter(prefix="/households/mealplans/rules", tags=["Households: Mealplan Rules"])


@controller(router)
class GroupMealplanConfigController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.group_meal_plan_rules

    @cached_property
    def mixins(self):
        return HttpRepo[PlanRulesCreate, PlanRulesOut, PlanRulesOut](self.repo, self.logger)

    @router.get("", response_model=PlanRulesPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=PlanRulesOut,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=PlanRulesOut, status_code=201)
    def create_one(self, data: PlanRulesCreate):
        save = mapper.cast(data, PlanRulesSave, group_id=self.group.id, household_id=self.household.id)
        return self.mixins.create_one(save)

    @router.get("/{item_id}", response_model=PlanRulesOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=PlanRulesOut)
    def update_one(self, item_id: UUID4, data: PlanRulesCreate):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=PlanRulesOut)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)  # type: ignore
