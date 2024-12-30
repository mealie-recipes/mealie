from datetime import UTC, datetime

from sqlalchemy import select

from mealie.db.models.household import GroupMealPlan
from mealie.schema.meal_plan.new_meal import ReadPlanEntry

from .repository_generic import HouseholdRepositoryGeneric


class RepositoryMeals(HouseholdRepositoryGeneric[ReadPlanEntry, GroupMealPlan]):
    def get_today(self, tz=UTC) -> list[ReadPlanEntry]:
        if not self.household_id:
            raise Exception("household_id not set")

        today = datetime.now(tz=tz).date()
        stmt = select(GroupMealPlan).filter(
            GroupMealPlan.date == today, GroupMealPlan.household_id == self.household_id
        )
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.model_validate(x) for x in plans]

    def get_meals_by_date_range(self, start_date: datetime, end_date: datetime) -> list[ReadPlanEntry]:
        if not self.household_id:
            raise Exception("household_id not set")

        stmt = select(GroupMealPlan).filter(
            GroupMealPlan.date >= start_date.date(),
            GroupMealPlan.date <= end_date.date(),
            GroupMealPlan.household_id == self.household_id,
        )
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.model_validate(x) for x in plans]
