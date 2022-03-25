from __future__ import annotations

from typing import Optional

from pydantic import UUID4

from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit


class ShoppingListItemRecipeRef(MealieModel):
    recipe_id: UUID4
    recipe_quantity: float


class ShoppingListItemRecipeRefOut(ShoppingListItemRecipeRef):
    id: UUID4
    shopping_list_item_id: UUID4

    class Config:
        orm_mode = True


class ShoppingListItemCreate(MealieModel):
    shopping_list_id: UUID4
    checked: bool = False
    position: int = 0

    is_food: bool = False

    note: Optional[str] = ""
    quantity: float = 1
    unit_id: UUID4 = None
    unit: Optional[IngredientUnit]
    food_id: UUID4 = None
    food: Optional[IngredientFood]

    label_id: Optional[UUID4] = None
    recipe_references: list[ShoppingListItemRecipeRef] = []


class ShoppingListItemUpdate(ShoppingListItemCreate):
    id: UUID4


class ShoppingListItemOut(ShoppingListItemUpdate):
    label: Optional[MultiPurposeLabelSummary]
    recipe_references: list[ShoppingListItemRecipeRefOut] = []

    class Config:
        orm_mode = True


class ShoppingListCreate(MealieModel):
    name: str = None


class ShoppingListRecipeRefOut(MealieModel):
    id: UUID4
    shopping_list_id: UUID4
    recipe_id: UUID4
    recipe_quantity: float
    recipe: RecipeSummary

    class Config:
        orm_mode = True


class ShoppingListSave(ShoppingListCreate):
    group_id: UUID4


class ShoppingListSummary(ShoppingListSave):
    id: UUID4

    class Config:
        orm_mode = True


class ShoppingListUpdate(ShoppingListSummary):
    list_items: list[ShoppingListItemOut] = []


class ShoppingListOut(ShoppingListUpdate):
    recipe_references: list[ShoppingListRecipeRefOut]

    class Config:
        orm_mode = True


from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSummary
from mealie.schema.recipe.recipe import RecipeSummary

ShoppingListRecipeRefOut.update_forward_refs()
ShoppingListItemOut.update_forward_refs()
