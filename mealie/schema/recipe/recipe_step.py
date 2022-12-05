from uuid import UUID, uuid4

from pydantic import UUID4, Field

from mealie.schema._mealie import MealieModel


class IngredientReferences(MealieModel):
    """
    A list of ingredient references.
    """

    reference_id: UUID4 | None

    class Config:
        orm_mode = True


class RecipeStep(MealieModel):
    id: UUID | None = Field(default_factory=uuid4)
    title: str | None = ""
    text: str
    ingredient_references: list[IngredientReferences] = []

    class Config:
        orm_mode = True
