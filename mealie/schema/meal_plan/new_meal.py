from datetime import date
from enum import Enum
from uuid import UUID

from pydantic import ConfigDict, field_validator
from pydantic_core.core_schema import ValidationInfo
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.group import GroupMealPlan
from mealie.db.models.recipe import RecipeModel
from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.response.pagination import PaginationBase


class PlanEntryType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    side = "side"


class CreateRandomEntry(MealieModel):
    date: date
    entry_type: PlanEntryType = PlanEntryType.dinner


class CreatePlanEntry(MealieModel):
    date: date
    entry_type: PlanEntryType = PlanEntryType.breakfast
    title: str = ""
    text: str = ""
    recipe_id: UUID | None

    @field_validator("recipe_id", always=True)
    @classmethod
    def id_or_title(cls, value, info: ValidationInfo):
        if bool(value) is False and bool(info.data["title"]) is False:
            raise ValueError(f"`recipe_id={value}` or `title={info.data['title']}` must be provided")

        return value


class UpdatePlanEntry(CreatePlanEntry):
    id: int
    group_id: UUID
    user_id: UUID | None


class SavePlanEntry(CreatePlanEntry):
    group_id: UUID
    user_id: UUID | None
    model_config = ConfigDict(from_attributes=True)


class ReadPlanEntry(UpdatePlanEntry):
    recipe: RecipeSummary | None
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(GroupMealPlan.recipe).joinedload(RecipeModel.recipe_category),
            selectinload(GroupMealPlan.recipe).joinedload(RecipeModel.tags),
            selectinload(GroupMealPlan.recipe).joinedload(RecipeModel.tools),
        ]


class PlanEntryPagination(PaginationBase):
    items: list[ReadPlanEntry]
