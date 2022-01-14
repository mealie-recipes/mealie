from __future__ import annotations

from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import UUID4

from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit


class ShoppingListItemCreate(CamelModel):
    shopping_list_id: UUID4
    checked: bool = False
    position: int = 0

    is_food: bool = False

    note: Optional[str] = ""
    quantity: float = 1
    unit_id: int = None
    unit: IngredientUnit = None
    food_id: int = None
    food: IngredientFood = None
    recipe_id: Optional[int] = None

    label_id: Optional[UUID4] = None


class ShoppingListItemOut(ShoppingListItemCreate):
    id: UUID4
    label: Optional[MultiPurposeLabelSummary]

    class Config:
        orm_mode = True


class ShoppingListCreate(CamelModel):
    name: str = None


class ShoppingListSave(ShoppingListCreate):
    group_id: UUID4


class ShoppingListSummary(ShoppingListSave):
    id: UUID4

    class Config:
        orm_mode = True


class ShoppingListUpdate(ShoppingListSummary):
    list_items: list[ShoppingListItemOut] = []


class ShoppingListOut(ShoppingListUpdate):
    class Config:
        orm_mode = True


from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSummary

ShoppingListItemOut.update_forward_refs()
