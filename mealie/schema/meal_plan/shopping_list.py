from pydantic import ConfigDict

from mealie.schema._mealie import MealieModel
from mealie.schema.user.user import GroupBase


class ListItem(MealieModel):
    title: str | None = None
    text: str = ""
    quantity: int = 1
    checked: bool = False
    model_config = ConfigDict(from_attributes=True)


class ShoppingListIn(MealieModel):
    name: str
    group: GroupBase | None = None
    items: list[ListItem]


class ShoppingListOut(ShoppingListIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
