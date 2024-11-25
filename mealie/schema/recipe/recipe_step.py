from uuid import UUID, uuid4

from pydantic import UUID4, ConfigDict, Field

from mealie.schema._mealie import MealieModel


class IngredientReferences(MealieModel):
    """
    A list of ingredient references.
    """

    reference_id: UUID4 | None = None
    model_config = ConfigDict(from_attributes=True)


class RecipeStep(MealieModel):
    id: UUID | None = Field(default_factory=uuid4)
    title: str | None = ""  # This is the section title!!!
    summary: str | None = ""
    text: str
    ingredient_references: list[IngredientReferences] = []
    model_config = ConfigDict(from_attributes=True)
