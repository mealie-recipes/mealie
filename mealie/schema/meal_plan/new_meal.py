from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import validator

from mealie.schema.recipe.recipe import RecipeSummary


class PlanEntryType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    side = "side"


class CreatRandomEntry(CamelModel):
    date: date
    entry_type: PlanEntryType = PlanEntryType.dinner


class CreatePlanEntry(CamelModel):
    date: date
    entry_type: PlanEntryType = PlanEntryType.breakfast
    title: str = ""
    text: str = ""
    recipe_id: Optional[UUID]

    @validator("recipe_id", always=True)
    @classmethod
    def id_or_title(cls, value, values):
        if bool(value) is False and bool(values["title"]) is False:
            raise ValueError(f"`recipe_id={value}` or `title={values['title']}` must be provided")

        return value


class UpdatePlanEntry(CreatePlanEntry):
    id: int
    group_id: UUID


class SavePlanEntry(CreatePlanEntry):
    group_id: UUID

    class Config:
        orm_mode = True


class ReadPlanEntry(UpdatePlanEntry):
    recipe: Optional[RecipeSummary]

    class Config:
        orm_mode = True
