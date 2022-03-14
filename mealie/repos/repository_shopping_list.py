from pydantic import UUID4

from mealie.db.models.group.shopping_list import ShoppingList
from mealie.schema.group.group_shopping_list import ShoppingListOut, ShoppingListUpdate

from .repository_generic import RepositoryGeneric


class RepositoryShoppingList(RepositoryGeneric[ShoppingListOut, ShoppingList]):
    def update(self, item_id: UUID4, data: ShoppingListUpdate) -> ShoppingListOut:  # type: ignore
        return super().update(item_id, data)
