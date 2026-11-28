from datetime import UTC, date, datetime
from typing import Any

from pydantic import UUID4, BaseModel
from sqlalchemy import or_, select

from mealie.core.exceptions import MealPlanEntriesChanged
from mealie.db.models.household import GroupMealPlan
from mealie.schema.meal_plan.new_meal import PlanEntryOut, PlanEntryReorderUpdate, PlanEntryType

from .repository_generic import HouseholdRepositoryGeneric


class RepositoryMeals(HouseholdRepositoryGeneric[PlanEntryOut, GroupMealPlan]):
    def update(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> PlanEntryOut:
        new_data = new_data.copy() if isinstance(new_data, dict) else new_data.model_dump()
        current_entry = self._query_one(match_value=match_value)
        # The plan's household comes from its user, so a client-supplied user_id could move it to another household
        new_data["user_id"] = current_entry.user_id

        new_date = new_data.get("date", current_entry.date)
        new_end_date = new_data.get("end_date", current_entry.end_date)
        # end_date = None => meal is scheduled on a specific weekday
        schedule_changed = new_date != current_entry.date or (new_end_date is not None) != (
            current_entry.end_date is not None
        )

        if schedule_changed:
            previous_date = current_entry.date
            previous_is_week = current_entry.end_date is not None
            new_data["position"] = self._insert_position(
                new_date,
                new_end_date,
                new_data.get("entry_type", current_entry.entry_type),
            )
            current_entry.date = new_date
            current_entry.end_date = new_end_date
            self.session.flush()
            self._renumber_positions_in_source_list(previous_date, previous_is_week)

        return super().update(match_value, new_data)

    def _insert_position(self, date_value: date, end_date_value: date | None, entry_type: str) -> int:
        if not self.household_id:
            raise Exception("household_id not set")

        entries = self.session.scalars(
            select(GroupMealPlan)
            # select the destination list: day entries when end_date_value is None, or week entries otherwise
            .where(
                GroupMealPlan.date == date_value,
                GroupMealPlan.end_date.is_not(None) if end_date_value is not None else GroupMealPlan.end_date.is_(None),
                GroupMealPlan.household_id == self.household_id,
            )
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

    def _renumber_positions_in_source_list(self, date_value: date, is_week: bool) -> None:
        entries = self.session.scalars(
            select(GroupMealPlan)
            .where(
                GroupMealPlan.date == date_value,
                GroupMealPlan.end_date.is_not(None) if is_week else GroupMealPlan.end_date.is_(None),
                GroupMealPlan.household_id == self.household_id,
            )
            .order_by(GroupMealPlan.position, GroupMealPlan.id)
        ).all()
        for position, entry in enumerate(entries):
            entry.position = position

    def create(self, data: PlanEntryOut | BaseModel | dict[str, Any]) -> PlanEntryOut:
        data = data if isinstance(data, dict) else data.model_dump()
        data["position"] = self._insert_position(
            data["date"], data.get("end_date"), data.get("entry_type", PlanEntryType.breakfast)
        )
        return super().create(data)

    def reorder(self, days: list[PlanEntryReorderUpdate]) -> None:
        if not self.household_id:
            raise Exception("household_id not set")

        requested_ids = [entry_id for day in days for entry_id in day.entry_ids]
        position_buckets = [
            (GroupMealPlan.date == day.date)
            & (GroupMealPlan.end_date.is_not(None) if day.end_date is not None else GroupMealPlan.end_date.is_(None))
            for day in days
        ]

        entries = (
            self.session.execute(
                select(GroupMealPlan).where(
                    or_(*position_buckets),
                    GroupMealPlan.household_id == self.household_id,
                )
            )
            .scalars()
            .all()
        )
        entries_by_id = {entry.id: entry for entry in entries}
        if set(requested_ids) != set(entries_by_id):
            raise MealPlanEntriesChanged

        try:
            for day in days:
                for position, entry_id in enumerate(day.entry_ids):
                    entry = entries_by_id[entry_id]
                    entry.date = day.date
                    entry.end_date = day.end_date
                    entry.position = position

            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def get_today(self, tz=UTC) -> list[PlanEntryOut]:
        if not self.household_id:
            raise Exception("household_id not set")

        today = datetime.now(tz=tz).date()
        stmt = (
            select(GroupMealPlan)
            .filter(
                GroupMealPlan.date == today,
                GroupMealPlan.end_date.is_(None),  # week entries aren't planned for a specific day
                GroupMealPlan.household_id == self.household_id,
            )
            .order_by(GroupMealPlan.position)
        )
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.model_validate(x) for x in plans]

    def get_meals_by_date_range(self, start_date: datetime, end_date: datetime) -> list[PlanEntryOut]:
        if not self.household_id:
            raise Exception("household_id not set")

        stmt = (
            select(GroupMealPlan)
            .filter(
                GroupMealPlan.date >= start_date.date(),
                GroupMealPlan.date <= end_date.date(),
                GroupMealPlan.end_date.is_(None),  # week entries aren't planned for a specific day
                GroupMealPlan.household_id == self.household_id,
            )
            .order_by(GroupMealPlan.date, GroupMealPlan.position)
        )
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.model_validate(x) for x in plans]
