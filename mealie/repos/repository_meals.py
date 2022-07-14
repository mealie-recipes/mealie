from datetime import date
from uuid import UUID

from mealie.db.models.group import GroupMealPlan
from mealie.schema.meal_plan.new_meal import ReadPlanEntry

from .repository_generic import RepositoryGeneric


class RepositoryMeals(RepositoryGeneric[ReadPlanEntry, GroupMealPlan]):
    def by_group(self, group_id: UUID) -> "RepositoryMeals":
        return super().by_group(group_id)  # type: ignore

    def get_today(self, group_id: UUID) -> list[ReadPlanEntry]:
        today = date.today()
        qry = self.session.query(GroupMealPlan).filter(GroupMealPlan.date == today, GroupMealPlan.group_id == group_id)

        return [self.schema.from_orm(x) for x in qry.all()]
