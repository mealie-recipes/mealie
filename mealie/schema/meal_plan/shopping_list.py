from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic.utils import GetterDict

from mealie.db.models.group.shopping_list import ShoppingListModel


class ListItem(CamelModel):
    title: Optional[str]
    text: str = ""
    quantity: int = 1
    checked: bool = False

    class Config:
        orm_mode = True


class ShoppingList(CamelModel):
    name: str
    group_id: int
    items: list[ListItem]
    id: int

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, ormModel: ShoppingListModel):
            return {**GetterDict(ormModel)}
