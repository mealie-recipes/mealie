from functools import cached_property

from pydantic import UUID4

from mealie.routes._base.abc_controller import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import CrudMixins
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema import mapper
from mealie.schema.meal_plan.plan_rules import PlanRulesCreate, PlanRulesOut, PlanRulesSave

router = UserAPIRouter(prefix="/groups/mealplans/rules", tags=["Groups: Mealplan Rules"])


@controller(router)
class GroupMealplanConfigController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.group_meal_plan_rules.by_group(self.group_id)

    @cached_property
    def mixins(self):
        return CrudMixins[PlanRulesCreate, PlanRulesOut, PlanRulesOut](self.repo, self.deps.logger)

    @router.get("", response_model=list[PlanRulesOut])
    def get_all(self):
        return self.repo.get_all(override_schema=PlanRulesOut)

    @router.post("", response_model=PlanRulesOut, status_code=201)
    def create_one(self, data: PlanRulesCreate):
        save = mapper.cast(data, PlanRulesSave, group_id=self.group.id)
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
