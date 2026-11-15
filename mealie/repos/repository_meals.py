from datetime import UTC, datetime

from pydantic import UUID4, BaseModel
from sqlalchemy import select

from mealie.db.models.household import GroupMealPlan
from mealie.schema.meal_plan.new_meal import PlanEntryOut

from .repository_generic import HouseholdRepositoryGeneric


class RepositoryMeals(HouseholdRepositoryGeneric[PlanEntryOut, GroupMealPlan]):
    def update(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> PlanEntryOut:
        # The plan's household comes from its user, so a client-supplied user_id could move it to another household
        new_data = new_data if isinstance(new_data, dict) else new_data.model_dump()
        new_data["user_id"] = self._query_one(match_value=match_value).user_id
        return super().update(match_value, new_data)

    def get_today(self, tz=UTC) -> list[PlanEntryOut]:
        if not self.household_id:
            raise Exception("household_id not set")

        today = datetime.now(tz=tz).date()
        stmt = select(GroupMealPlan).filter(
            GroupMealPlan.date == today,
            GroupMealPlan.end_date.is_(None),  # week entries aren't planned for a specific day
            GroupMealPlan.household_id == self.household_id,
        )
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.model_validate(x) for x in plans]

    def get_meals_by_date_range(self, start_date: datetime, end_date: datetime) -> list[PlanEntryOut]:
        if not self.household_id:
            raise Exception("household_id not set")

        stmt = select(GroupMealPlan).filter(
            GroupMealPlan.date >= start_date.date(),
            GroupMealPlan.date <= end_date.date(),
            GroupMealPlan.end_date.is_(None),  # week entries aren't planned for a specific day
            GroupMealPlan.household_id == self.household_id,
        )
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.model_validate(x) for x in plans]
