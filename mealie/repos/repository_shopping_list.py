from pydantic import UUID4

from mealie.db.models.group.shopping_list import ShoppingList, ShoppingListItem
from mealie.schema.group.group_shopping_list import ShoppingListOut, ShoppingListUpdate

from .repository_generic import RepositoryGeneric


class RepositoryShoppingList(RepositoryGeneric[ShoppingListOut, ShoppingList]):
    def _consolidate(self, item_list: list[ShoppingListItem]) -> ShoppingListItem:
        """
        consolidate itterates through the shopping list provided and returns
        a consolidated list where all items that are matched against multiple values are
        de-duplicated and only the first item is kept where the quantity is updated accoridngly.
        """

        def can_merge(item1: ShoppingListItem, item2: ShoppingListItem) -> bool:
            """
            can_merge checks if the two items can be merged together.
            """
            can_merge_return = False

            # If the items have the same food and unit they can be merged.
            if item1.unit == item2.unit and item1.food == item2.food:
                can_merge_return = True

            # If no food or units are present check against the notes field.
            if not all([item1.food, item1.unit, item2.food, item2.unit]):
                can_merge_return = item1.note == item2.note

            # Otherwise Assume They Can't Be Merged

            return can_merge_return

        consolidated_list: list[ShoppingListItem] = []
        checked_items: list[int] = []

        for base_index, base_item in enumerate(item_list):
            if base_index in checked_items:
                continue

            checked_items.append(base_index)
            for inner_index, inner_item in enumerate(item_list):
                if inner_index in checked_items:
                    continue
                if can_merge(base_item, inner_item):
                    base_item.quantity += inner_item.quantity
                    checked_items.append(inner_index)

            consolidated_list.append(base_item)

        return consolidated_list

    def update(self, item_id: UUID4, data: ShoppingListUpdate) -> ShoppingListOut:
        """
        update updates the shopping list item with the provided data.
        """
        data.list_items = self._consolidate(data.list_items)
        return super().update(item_id, data)
