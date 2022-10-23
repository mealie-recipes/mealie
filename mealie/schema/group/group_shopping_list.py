from __future__ import annotations

from datetime import datetime

from pydantic import UUID4
from pydantic.utils import GetterDict

from mealie.db.models.group.shopping_list import ShoppingList, ShoppingListItem
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.types import NoneFloat
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit
from mealie.schema.response.pagination import PaginationBase


class ShoppingListItemRecipeRef(MealieModel):
    recipe_id: UUID4
    recipe_quantity: NoneFloat = 0


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

    note: str | None = ""
    quantity: float = 1
    unit_id: UUID4 | None = None
    unit: IngredientUnit | None
    food_id: UUID4 | None = None
    food: IngredientFood | None

    label_id: UUID4 | None = None
    recipe_references: list[ShoppingListItemRecipeRef] = []
    extras: dict | None = {}

    created_at: datetime | None
    update_at: datetime | None


class ShoppingListItemUpdate(ShoppingListItemCreate):
    id: UUID4


class ShoppingListItemOut(ShoppingListItemUpdate):
    label: MultiPurposeLabelSummary | None
    recipe_references: list[ShoppingListItemRecipeRef | ShoppingListItemRecipeRefOut] = []

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, name_orm: ShoppingListItem):
            return {
                **GetterDict(name_orm),
                "extras": {x.key_name: x.value for x in name_orm.extras},
            }


class ShoppingListCreate(MealieModel):
    name: str | None = None
    extras: dict | None = {}

    created_at: datetime | None
    update_at: datetime | None


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

        @classmethod
        def getter_dict(cls, name_orm: ShoppingList):
            return {
                **GetterDict(name_orm),
                "extras": {x.key_name: x.value for x in name_orm.extras},
            }


class ShoppingListPagination(PaginationBase):
    items: list[ShoppingListSummary]


class ShoppingListUpdate(ShoppingListSummary):
    list_items: list[ShoppingListItemOut] = []


class ShoppingListOut(ShoppingListUpdate):
    recipe_references: list[ShoppingListRecipeRefOut]

    class Config:
        orm_mode = True


from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSummary  # noqa: E402
from mealie.schema.recipe.recipe import RecipeSummary  # noqa: E402

ShoppingListRecipeRefOut.update_forward_refs()
ShoppingListItemOut.update_forward_refs()
