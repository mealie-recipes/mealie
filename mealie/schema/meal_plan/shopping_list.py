from mealie.schema._mealie import MealieModel
from mealie.schema.getter_dict import GroupGetterDict
from pydantic import ConfigDict


class ListItem(MealieModel):
    title: str | None
    text: str = ""
    quantity: int = 1
    checked: bool = False
    model_config = ConfigDict(from_attributes=True)


class ShoppingListIn(MealieModel):
    name: str
    group: str | None
    items: list[ListItem]


class ShoppingListOut(ShoppingListIn):
    id: int
    # TODO[pydantic]: The following keys were removed: `getter_dict`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, getter_dict=GroupGetterDict)
