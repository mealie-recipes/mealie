from sqlalchemy import or_, select

from mealie.db.models.household.mealplan import GroupMealPlanRules
from mealie.schema.meal_plan.plan_rules import PlanRulesDay, PlanRulesOut, PlanRulesType

from .repository_generic import HouseholdRepositoryGeneric


class RepositoryMealPlanRules(HouseholdRepositoryGeneric[PlanRulesOut, GroupMealPlanRules]):
    def get_rules(self, day: PlanRulesDay, entry_type: PlanRulesType) -> list[PlanRulesOut]:
        stmt = select(GroupMealPlanRules).filter(
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

        if self.group_id:
            stmt = stmt.filter(GroupMealPlanRules.group_id == self.group_id)
        if self.household_id:
            stmt = stmt.filter(GroupMealPlanRules.household_id == self.household_id)

        rules = self.session.execute(stmt).scalars().all()

        return [self.schema.model_validate(x) for x in rules]
