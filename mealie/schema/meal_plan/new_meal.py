import datetime
from datetime import date, timedelta
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator
from pydantic_core.core_schema import ValidationInfo
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.household import GroupMealPlan
from mealie.db.models.recipe import RecipeModel
from mealie.db.models.users.users import User
from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.response.pagination import PaginationBase


class PlanEntryType(StrEnum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    side = "side"
    snack = "snack"
    drink = "drink"
    dessert = "dessert"


WEEK_ENTRY_LENGTH = timedelta(days=6)
"""How far `end_date` is from `date` on an entry planned for a week instead of a specific day"""


def validate_end_date(value: date | None, info: ValidationInfo) -> date | None:
    """Only single-day entries (no `end_date`) and week entries are supported"""
    start = info.data.get("date")
    if value is not None and start is not None and value != start + WEEK_ENTRY_LENGTH:
        raise ValueError(f"`end_date` must be empty or {WEEK_ENTRY_LENGTH.days} days after `date`")

    return value


class CreateRandomEntry(MealieModel):
    date: date
    end_date: datetime.date | None = None
    entry_type: PlanEntryType = PlanEntryType.dinner

    _validate_end_date = field_validator("end_date")(validate_end_date)


class CreatePlanEntry(MealieModel):
    date: date
    end_date: datetime.date | None = None
    entry_type: PlanEntryType = PlanEntryType.breakfast
    title: str = ""
    text: str = ""
    recipe_id: Annotated[UUID | None, Field(validate_default=True)] = None
    recipe_scale: Annotated[float, Field(gt=0)] = 1.0

    @field_validator("recipe_id")
    @classmethod
    def id_or_title(cls, value, info: ValidationInfo):
        if bool(value) is False and bool(info.data["title"]) is False:
            raise ValueError(f"`recipe_id={value}` or `title={info.data['title']}` must be provided")

        return value

    _validate_end_date = field_validator("end_date")(validate_end_date)


class UpdatePlanEntry(CreatePlanEntry):
    id: int
    group_id: UUID
    user_id: UUID


class SavePlanEntry(CreatePlanEntry):
    group_id: UUID
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)


class ReadPlanEntry(UpdatePlanEntry):
    household_id: UUID
    recipe: RecipeSummary | None = None
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(GroupMealPlan.recipe).joinedload(RecipeModel.recipe_category),
            selectinload(GroupMealPlan.recipe).joinedload(RecipeModel.tags),
            selectinload(GroupMealPlan.recipe).joinedload(RecipeModel.tools),
            selectinload(GroupMealPlan.user).load_only(User.household_id),
        ]


class PlanEntryPagination(PaginationBase):
    items: list[ReadPlanEntry]
