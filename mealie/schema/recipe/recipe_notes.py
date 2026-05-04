from uuid import UUID, uuid4

from pydantic import ConfigDict, Field, field_validator

from mealie.schema._mealie import MealieModel


class RecipeNote(MealieModel):
    title: str
    text: str
    reference_id: UUID = Field(default_factory=uuid4)
    model_config = ConfigDict(from_attributes=True)

    @field_validator("reference_id", mode="before")
    @classmethod
    def ensure_reference_id(cls, value) -> UUID:
        return value or uuid4()
