from uuid import UUID

from sqlalchemy import or_

from mealie.db.models.group.mealplan import GroupMealPlanRules
from mealie.schema.meal_plan.plan_rules import PlanRulesDay, PlanRulesOut, PlanRulesType

from .repository_generic import RepositoryGeneric


class RepositoryMealPlanRules(RepositoryGeneric[PlanRulesOut, GroupMealPlanRules]):
    def by_group(self, group_id: UUID) -> "RepositoryMealPlanRules":
        return super().by_group(group_id)  # type: ignore

    def get_rules(self, day: PlanRulesDay, entry_type: PlanRulesType) -> list[PlanRulesOut]:
        qry = self.session.query(GroupMealPlanRules).filter(
            or_(
                GroupMealPlanRules.day == day,
                GroupMealPlanRules.day.is_(None),
                GroupMealPlanRules.day == PlanRulesDay.unset.value,
            ),
            or_(
                GroupMealPlanRules.entry_type == entry_type,
                GroupMealPlanRules.entry_type.is_(None),
                GroupMealPlanRules.entry_type == PlanRulesType.unset.value,
            ),
        )

        return [self.schema.from_orm(x) for x in qry.all()]
