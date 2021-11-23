from typing import Optional
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import Field


class IngredientReferences(CamelModel):
    """
    A list of ingredient references.
    """

    reference_id: UUID = None

    class Config:
        orm_mode = True


class RecipeStep(CamelModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    title: Optional[str] = ""
    text: str
    ingredient_references: list[IngredientReferences] = []

    class Config:
        orm_mode = True
