from __future__ import annotations

from fastapi_camelcase import CamelModel
from pydantic import UUID4


class MultiPurposeLabelCreate(CamelModel):
    name: str
    color: str = "#E0E0E0"


class MultiPurposeLabelSave(MultiPurposeLabelCreate):
    group_id: UUID4


class MultiPurposeLabelUpdate(MultiPurposeLabelSave):
    id: UUID4


class MultiPurposeLabelSummary(MultiPurposeLabelUpdate):
    pass

    class Config:
        orm_mode = True


class MultiPurposeLabelOut(MultiPurposeLabelUpdate):
    # shopping_list_items: list[ShoppingListItemOut] = []
    # foods: list[IngredientFood] = []

    class Config:
        orm_mode = True


# from mealie.schema.recipe.recipe_ingredient import IngredientFood
# from mealie.schema.group.group_shopping_list import ShoppingListItemOut

# MultiPurposeLabelOut.update_forward_refs()
