from mealie.schema._mealie import MealieModel
from mealie.schema.getter_dict import GroupGetterDict


class ListItem(MealieModel):
    title: str | None
    text: str = ""
    quantity: int = 1
    checked: bool = False

    class Config:
        orm_mode = True


class ShoppingListIn(MealieModel):
    name: str
    group: str | None
    items: list[ListItem]


class ShoppingListOut(ShoppingListIn):
    id: int

    class Config:
        orm_mode = True
        getter_dict = GroupGetterDict
