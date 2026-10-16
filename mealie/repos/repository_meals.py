from datetime import UTC, date, datetime
from typing import Any

from fastapi import HTTPException
from pydantic import UUID4, BaseModel
from sqlalchemy import select

from mealie.db.models.household import GroupMealPlan
from mealie.schema.meal_plan.new_meal import PlanEntryType, ReadPlanEntry, ReorderPlanEntriesByDay

from .repository_generic import HouseholdRepositoryGeneric


class RepositoryMeals(HouseholdRepositoryGeneric[ReadPlanEntry, GroupMealPlan]):
    def _insert_position(self, date_value: date, entry_type: str) -> int:
        if not self.household_id:
            raise Exception("household_id not set")

        entries = self.session.scalars(
            select(GroupMealPlan)
            .where(GroupMealPlan.date == date_value, GroupMealPlan.household_id == self.household_id)
            .order_by(GroupMealPlan.position, GroupMealPlan.id)
        ).all()
        type_order = {plan_type.value: rank for rank, plan_type in enumerate(PlanEntryType)}
        # Preserve manual order: join the last matching type, otherwise precede a later type.
        matching = [i for i, entry in enumerate(entries) if entry.entry_type == entry_type]
        if matching:
            position = matching[-1] + 1
        else:
            new_type_rank = type_order.get(entry_type, len(type_order))
            position = len(entries)
            for i, entry in enumerate(entries):
                existing_type_rank = type_order.get(entry.entry_type, len(type_order))
                if existing_type_rank > new_type_rank:
                    position = i
                    break
        # shift the affected positions to make a gap
        for i, entry in enumerate(entries):
            entry.position = i if i < position else i + 1
        return position

    def _renumber_positions(self, date_value: date) -> None:
        entries = self.session.scalars(
            select(GroupMealPlan)
            .where(GroupMealPlan.date == date_value, GroupMealPlan.household_id == self.household_id)
            .order_by(GroupMealPlan.position, GroupMealPlan.id)
        ).all()
        for position, entry in enumerate(entries):
            entry.position = position

    def create(self, data: ReadPlanEntry | BaseModel | dict[str, Any]) -> ReadPlanEntry:
        data = data if isinstance(data, dict) else data.model_dump()
        data["position"] = self._insert_position(data["date"], data.get("entry_type", PlanEntryType.breakfast))
        return super().create(data)

    def update(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> ReadPlanEntry:
        data = new_data if isinstance(new_data, dict) else new_data.model_dump()
        entry = self._query_one(match_value)
        date_value = data.get("date")

        if date_value is not None and date_value != entry.date:
            previous_date = entry.date
            data["position"] = self._insert_position(date_value, data.get("entry_type", entry.entry_type))
            entry.date = date_value
            # exclude the moved entry from the old day's query
            self.session.flush()
            self._renumber_positions(previous_date)

        return super().update(match_value, data)

    def reorder(self, days: list[ReorderPlanEntriesByDay]) -> None:
        if not self.household_id:
            raise Exception("household_id not set")
        if not days:
            raise HTTPException(status_code=422, detail="At least one day is required.")

        dates = [day.date for day in days]
        if len(set(dates)) != len(dates):
            raise HTTPException(status_code=422, detail="Each date may only be included once.")

        requested_ids = [entry_id for day in days for entry_id in day.entry_ids]
        if len(set(requested_ids)) != len(requested_ids):
            raise HTTPException(status_code=422, detail="A meal plan entry may only be included once.")

        entries = (
            self.session.execute(
                select(GroupMealPlan).where(
                    GroupMealPlan.date.in_(dates),
                    GroupMealPlan.household_id == self.household_id,
                )
            )
            .scalars()
            .all()
        )
        entries_by_id = {entry.id: entry for entry in entries}
        if set(requested_ids) != set(entries_by_id):
            raise HTTPException(status_code=409, detail="Meal plan entries changed. Refresh and try again.")

        try:
            for day in days:
                for position, entry_id in enumerate(day.entry_ids):
                    entry = entries_by_id[entry_id]
                    entry.date = day.date
                    entry.position = position

            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def get_today(self, tz=UTC) -> list[ReadPlanEntry]:
        if not self.household_id:
            raise Exception("household_id not set")

        today = datetime.now(tz=tz).date()
        stmt = (
            select(GroupMealPlan)
            .filter(GroupMealPlan.date == today, GroupMealPlan.household_id == self.household_id)
            .order_by(GroupMealPlan.position)
        )
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.model_validate(x) for x in plans]

    def get_meals_by_date_range(self, start_date: datetime, end_date: datetime) -> list[ReadPlanEntry]:
        if not self.household_id:
            raise Exception("household_id not set")

        stmt = (
            select(GroupMealPlan)
            .filter(
                GroupMealPlan.date >= start_date.date(),
                GroupMealPlan.date <= end_date.date(),
                GroupMealPlan.household_id == self.household_id,
            )
            .order_by(GroupMealPlan.date, GroupMealPlan.position)
        )
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.model_validate(x) for x in plans]
