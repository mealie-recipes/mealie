import enum
from typing import Optional, Union

from fastapi_camelcase import CamelModel


class CreateIngredientFood(CamelModel):
    name: str
    description: str = ""


class CreateIngredientUnit(CreateIngredientFood):
    fraction: bool = True
    abbreviation: str = ""


class IngredientFood(CreateIngredientFood):
    id: int

    class Config:
        orm_mode = True


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
