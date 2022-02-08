from __future__ import annotations

import enum
from typing import Optional, Union
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import UUID4, Field


class UnitFoodBase(CamelModel):
    name: str
    description: str = ""


class CreateIngredientFood(UnitFoodBase):
    label_id: UUID4 = None


class SaveIngredientFood(CreateIngredientFood):
    group_id: UUID4


class IngredientFood(CreateIngredientFood):
    id: int
    label: MultiPurposeLabelSummary = None

    class Config:
        orm_mode = True


class CreateIngredientUnit(UnitFoodBase):
    fraction: bool = True
    abbreviation: str = ""


class SaveIngredientUnit(CreateIngredientUnit):
    group_id: UUID4


class IngredientUnit(CreateIngredientUnit):
    id: int

    class Config:
        orm_mode = True


class RecipeIngredient(CamelModel):
    title: Optional[str]
    note: Optional[str]
    unit: Optional[Union[IngredientUnit, CreateIngredientUnit]]
    food: Optional[Union[IngredientFood, CreateIngredientFood]]
    disable_amount: bool = True
    quantity: float = 1

    # Ref is used as a way to distinguish between an individual ingredient on the frontend
    # It is required for the reorder and section titles to function properly because of how
    # Vue handles reactivity. ref may serve another purpose in the future.
    reference_id: UUID = Field(default_factory=uuid4)

    class Config:
        orm_mode = True


class IngredientConfidence(CamelModel):
    average: float = None
    comment: float = None
    name: float = None
    unit: float = None
    quantity: float = None
    food: float = None


class ParsedIngredient(CamelModel):
    input: Optional[str]
    confidence: IngredientConfidence = IngredientConfidence()
    ingredient: RecipeIngredient


class RegisteredParser(str, enum.Enum):
    nlp = "nlp"
    brute = "brute"


class IngredientsRequest(CamelModel):
    parser: RegisteredParser = RegisteredParser.nlp
    ingredients: list[str]


class IngredientRequest(CamelModel):
    parser: RegisteredParser = RegisteredParser.nlp
    ingredient: str


from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSummary

IngredientFood.update_forward_refs()
