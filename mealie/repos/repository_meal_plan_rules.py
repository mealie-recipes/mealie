from uuid import UUID

from sqlalchemy import or_

from mealie.db.models.group.mealplan import GroupMealPlanRules
from mealie.schema.meal_plan.plan_rules import PlanRulesDay, PlanRulesOut, PlanRulesType

from .repository_generic import RepositoryGeneric


class RepositoryMealPlanRules(RepositoryGeneric[PlanRulesOut, GroupMealPlanRules]):
    def by_group(self, group_id: UUID) -> "RepositoryMealPlanRules":
        return super().by_group(group_id)

    def get_rules(self, day: PlanRulesDay, entry_type: PlanRulesType) -> list[PlanRulesOut]:
        qry = self.session.query(GroupMealPlanRules).filter(
            or_(
                GroupMealPlanRules.day.is_(day),
                GroupMealPlanRules.day.is_(None),
                GroupMealPlanRules.day.is_(PlanRulesDay.unset.value),
            ),
            or_(
                GroupMealPlanRules.entry_type.is_(entry_type),
                GroupMealPlanRules.entry_type.is_(None),
                GroupMealPlanRules.entry_type.is_(PlanRulesType.unset.value),
            ),
        )

        return [self.schema.from_orm(x) for x in qry.all()]
