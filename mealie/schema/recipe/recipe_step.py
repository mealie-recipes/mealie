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

    duration_seconds: int | None = Field(default=None, ge=1, le=2147483647, strict=True)

    @field_validator("duration_seconds", mode="before")
    @classmethod
    def normalize_duration(cls, value: Any) -> Any:
        if isinstance(value, bool):
            raise ValueError("Duration must be a whole number of seconds, not a boolean")
        if value == 0:
            return None
        # JSON 1, 1.0 and 1e0 express the same whole number. Never round a fraction.
        if isinstance(value, float) and 1 <= value <= 2147483647 and value.is_integer():
            return int(value)
        return value
