from fastapi_camelcase import CamelModel
from pydantic import UUID4

from mealie.schema.recipe import IngredientFood


class MultiPurposeLabelCreate(CamelModel):
    name: str
    color: str = ""


class MultiPurposeLabelSave(MultiPurposeLabelCreate):
    group_id: UUID4


class MultiPurposeLabelUpdate(MultiPurposeLabelSave):
    id: UUID4


class MultiPurposeLabelSummary(MultiPurposeLabelUpdate):
    pass

    class Config:
        orm_mode = True


class MultiPurposeLabelOut(MultiPurposeLabelUpdate):
    shopping_list_items: "list[ShoppingListItemOut]" = []
    foods: list[IngredientFood] = []

    class Config:
        orm_mode = True


from mealie.schema.group.group_shopping_list import ShoppingListItemOut

MultiPurposeLabelOut.update_forward_refs()
