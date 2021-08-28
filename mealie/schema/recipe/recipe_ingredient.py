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
    unit: Optional[Union[CreateIngredientUnit, IngredientUnit]]
    food: Optional[Union[CreateIngredientFood, IngredientFood]]
    disable_amount: bool = True
    quantity: float = 1

    class Config:
        orm_mode = True
