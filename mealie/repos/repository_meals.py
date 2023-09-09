from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import select

from mealie.db.models.group import GroupMealPlan
from mealie.schema.meal_plan.new_meal import ReadPlanEntry

from .repository_generic import RepositoryGeneric


class RepositoryMeals(RepositoryGeneric[ReadPlanEntry, GroupMealPlan]):
    def by_group(self, group_id: UUID) -> "RepositoryMeals":
        return super().by_group(group_id)

    def get_today(self, group_id: UUID) -> list[ReadPlanEntry]:
        return self.get_for_day(group_id, 0)

    def get_for_day(self, group_id: UUID, relative_day: int) -> list[ReadPlanEntry]:
        day = date.today() + timedelta(days=relative_day)
        stmt = select(GroupMealPlan).filter(GroupMealPlan.date == day, GroupMealPlan.group_id == group_id)
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.from_orm(x) for x in plans]
