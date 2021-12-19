from datetime import date
from uuid import UUID

from mealie.db.models.group import GroupMealPlan
from mealie.schema.meal_plan.new_meal import ReadPlanEntry

from .repository_generic import RepositoryGeneric


class RepositoryMeals(RepositoryGeneric[ReadPlanEntry, GroupMealPlan]):
    def get_slice(self, start: date, end: date, group_id: UUID) -> list[ReadPlanEntry]:
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        qry = self.session.query(GroupMealPlan).filter(
            GroupMealPlan.date.between(start, end),
            GroupMealPlan.group_id == group_id,
        )

        return [self.schema.from_orm(x) for x in qry.all()]

    def get_today(self, group_id: UUID) -> list[ReadPlanEntry]:
        today = date.today()
        qry = self.session.query(GroupMealPlan).filter(GroupMealPlan.date == today, GroupMealPlan.group_id == group_id)

        return [self.schema.from_orm(x) for x in qry.all()]
