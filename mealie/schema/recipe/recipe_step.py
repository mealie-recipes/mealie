from typing import Optional
from uuid import UUID

from fastapi_camelcase import CamelModel


class IngredientReferences(CamelModel):
    """
    A list of ingredient references.
    """

    reference_id: UUID = None

    class Config:
        orm_mode = True


class RecipeStep(CamelModel):
    title: Optional[str] = ""
    text: str
    ingredient_references: list[IngredientReferences] = []

    class Config:
        orm_mode = True
