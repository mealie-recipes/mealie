from pydantic import UUID4

from mealie.db.models.household.shopping_list import ShoppingList
from mealie.schema.household.group_shopping_list import ShoppingListOut, ShoppingListUpdate

from .repository_generic import HouseholdRepositoryGeneric


class RepositoryShoppingList(HouseholdRepositoryGeneric[ShoppingListOut, ShoppingList]):
    def update(self, item_id: UUID4, data: ShoppingListUpdate | dict) -> ShoppingListOut:  # type: ignore[override]
        return super().update(item_id, data)
