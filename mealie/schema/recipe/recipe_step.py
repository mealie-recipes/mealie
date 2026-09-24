from typing import Any
from uuid import UUID, uuid4

from pydantic import UUID4, ConfigDict, Field, field_validator

from mealie.schema._mealie import MealieModel


class IngredientReferences(MealieModel):
    """
    A list of ingredient references.
    """

    reference_id: UUID4 | None = None
    model_config = ConfigDict(from_attributes=True)


class NoteReference(MealieModel):
    reference_id: UUID4 | None = None
    model_config = ConfigDict(from_attributes=True)


class RecipeStep(MealieModel):
    id: UUID | None = Field(default_factory=uuid4)
    title: str | None = ""  # This is the section title!!!
    summary: str | None = ""
    text: str
    ingredient_references: list[IngredientReferences] = []
    note_references: list[NoteReference] = []
    model_config = ConfigDict(from_attributes=True)

    duration_minutes: int | None = Field(default=None, ge=1, le=2147483647)

    @field_validator("duration_minutes", mode="before")
    @classmethod
    def normalize_duration(cls, value: Any) -> Any:
        if value == 0:
            return None
        return value
