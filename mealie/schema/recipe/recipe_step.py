from uuid import UUID, uuid4

from pydantic import ConfigDict, UUID4, Field

from mealie.schema._mealie import MealieModel


class IngredientReferences(MealieModel):
    """
    A list of ingredient references.
    """

    reference_id: UUID4 | None
    model_config = ConfigDict(from_attributes=True)


class RecipeStep(MealieModel):
    id: UUID | None = Field(default_factory=uuid4)
    title: str | None = ""
    text: str
    ingredient_references: list[IngredientReferences] = []
    model_config = ConfigDict(from_attributes=True)
