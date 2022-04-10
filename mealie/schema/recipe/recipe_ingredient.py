from __future__ import annotations

import enum
from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import UUID4, Field

from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.types import NoneFloat


class UnitFoodBase(MealieModel):
    name: str
    description: str = ""


class CreateIngredientFood(UnitFoodBase):
    label_id: Optional[UUID4] = None


class SaveIngredientFood(CreateIngredientFood):
    group_id: UUID4


class IngredientFood(CreateIngredientFood):
    id: UUID4
    label: Optional[MultiPurposeLabelSummary] = None

    class Config:
        orm_mode = True


class CreateIngredientUnit(UnitFoodBase):
    fraction: bool = True
    abbreviation: str = ""


class SaveIngredientUnit(CreateIngredientUnit):
    group_id: UUID4


class IngredientUnit(CreateIngredientUnit):
    id: UUID4

    class Config:
        orm_mode = True


class RecipeIngredient(MealieModel):
    title: Optional[str]
    note: Optional[str]
    unit: Optional[Union[IngredientUnit, CreateIngredientUnit]]
    food: Optional[Union[IngredientFood, CreateIngredientFood]]
    disable_amount: bool = True
    quantity: float = 1
    original_text: Optional[str]

    # Ref is used as a way to distinguish between an individual ingredient on the frontend
    # It is required for the reorder and section titles to function properly because of how
    # Vue handles reactivity. ref may serve another purpose in the future.
    reference_id: UUID = Field(default_factory=uuid4)

    class Config:
        orm_mode = True


class IngredientConfidence(MealieModel):
    average: NoneFloat = None
    comment: NoneFloat = None
    name: NoneFloat = None
    unit: NoneFloat = None
    quantity: NoneFloat = None
    food: NoneFloat = None


class ParsedIngredient(MealieModel):
    input: Optional[str]
    confidence: IngredientConfidence = IngredientConfidence()
    ingredient: RecipeIngredient


class RegisteredParser(str, enum.Enum):
    nlp = "nlp"
    brute = "brute"


class IngredientsRequest(MealieModel):
    parser: RegisteredParser = RegisteredParser.nlp
    ingredients: list[str]


class IngredientRequest(MealieModel):
    parser: RegisteredParser = RegisteredParser.nlp
    ingredient: str


class IngredientMerge(MealieModel):
    from_food: UUID4
    to_food: UUID4


from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSummary

IngredientFood.update_forward_refs()
