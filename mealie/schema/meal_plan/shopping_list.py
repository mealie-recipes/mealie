from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic.utils import GetterDict

from mealie.db.models.shopping_list import ShoppingList


class ListItem(CamelModel):
    title: Optional[str]
    text: str = ""
    quantity: int = 1
    checked: bool = False

    class Config:
        orm_mode = True


class ShoppingListIn(CamelModel):
    name: str
    group: Optional[str]
    items: list[ListItem]


class ShoppingListOut(ShoppingListIn):
    id: int

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, ormModel: ShoppingList):
            return {
                **GetterDict(ormModel),
                "group": ormModel.group.name,
            }
