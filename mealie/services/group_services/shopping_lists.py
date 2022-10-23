from pydantic import UUID4

from mealie.core.exceptions import UnexpectedNone
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group import ShoppingListItemCreate, ShoppingListOut
from mealie.schema.group.group_shopping_list import (
    ShoppingListItemOut,
    ShoppingListItemRecipeRef,
    ShoppingListItemUpdate,
)


class ShoppingListService:
    def __init__(self, repos: AllRepositories):
        self.repos = repos
        self.shopping_lists = repos.group_shopping_lists
        self.list_items = repos.group_shopping_list_item
        self.list_item_refs = repos.group_shopping_list_item_references
        self.list_refs = repos.group_shopping_list_recipe_refs

    @staticmethod
    def can_merge(item1: ShoppingListItemOut, item2: ShoppingListItemOut) -> bool:
        """
        can_merge checks if the two items can be merged together.
        """

        # Check if foods are equal
        foods_is_none = item1.food_id is None and item2.food_id is None
        foods_not_none = not foods_is_none
        foods_equal = item1.food_id == item2.food_id

        # Check if units are equal
        units_is_none = item1.unit_id is None and item2.unit_id is None
        units_not_none = not units_is_none
        units_equal = item1.unit_id == item2.unit_id

        # Check if Notes are equal
        if foods_is_none and units_is_none:
            return item1.note == item2.note

        if foods_not_none and units_not_none:
            return foods_equal and units_equal

        if foods_not_none:
            return foods_equal

        return False

    def consolidate_list_items(self, item_list: list[ShoppingListItemOut]) -> list[ShoppingListItemOut]:
        """
        itterates through the shopping list provided and returns
        a consolidated list where all items that are matched against multiple values are
        de-duplicated and only the first item is kept where the quantity is updated accordingly.
        """

        consolidated_list: list[ShoppingListItemOut] = []
        checked_items: list[int] = []

        for base_index, base_item in enumerate(item_list):
            if base_index in checked_items:
                continue

            checked_items.append(base_index)
            for inner_index, inner_item in enumerate(item_list):
                if inner_index in checked_items:
                    continue
                if ShoppingListService.can_merge(base_item, inner_item):
                    # Set Quantity
                    base_item.quantity += inner_item.quantity

                    # Set References
                    new_refs = []
                    for ref in inner_item.recipe_references:
                        ref.shopping_list_item_id = base_item.id  # type: ignore
                        new_refs.append(ref)

                    base_item.recipe_references.extend(new_refs)
                    checked_items.append(inner_index)

            consolidated_list.append(base_item)

        return consolidated_list

    def consolidate_and_save(
        self, data: list[ShoppingListItemUpdate]
    ) -> tuple[list[ShoppingListItemOut], list[ShoppingListItemOut]]:
        """
        returns:
        - updated_shopping_list_items
        - deleted_shopping_list_items
        """
        # TODO: Convert to update many with single call

        all_updates = []
        all_deletes = []
        keep_ids = []

        for item in self.consolidate_list_items(data):  # type: ignore
            updated_data = self.list_items.update(item.id, item)
            all_updates.append(updated_data)
            keep_ids.append(updated_data.id)

        for item in data:  # type: ignore
            if item.id not in keep_ids:
                self.list_items.delete(item.id)
                all_deletes.append(item)

        return all_updates, all_deletes

    # =======================================================================
    # Methods

    def add_recipe_ingredients_to_list(
        self, list_id: UUID4, recipe_id: UUID4
    ) -> tuple[ShoppingListOut, list[ShoppingListItemOut], list[ShoppingListItemOut], list[ShoppingListItemOut]]:
        """
        returns:
            - updated_shopping_list
            - new_shopping_list_items
            - updated_shopping_list_items
            - deleted_shopping_list_items
        """
        recipe = self.repos.recipes.get_one(recipe_id, "id")
        if not recipe:
            raise UnexpectedNone("Recipe not found")

        to_create = []
        for ingredient in recipe.recipe_ingredient:
            food_id = None
            try:
                food_id = ingredient.food.id  # type: ignore
            except AttributeError:
                pass

            label_id = None
            try:
                label_id = ingredient.food.label.id  # type: ignore
            except AttributeError:
                pass

            unit_id = None
            try:
                unit_id = ingredient.unit.id  # type: ignore
            except AttributeError:
                pass

            to_create.append(
                ShoppingListItemCreate(
                    shopping_list_id=list_id,
                    is_food=not recipe.settings.disable_amount if recipe.settings else False,
                    food_id=food_id,
                    unit_id=unit_id,
                    quantity=ingredient.quantity,
                    note=ingredient.note,
                    label_id=label_id,
                    recipe_id=recipe_id,
                    recipe_references=[
                        ShoppingListItemRecipeRef(
                            recipe_id=recipe_id,
                            recipe_quantity=ingredient.quantity,
                        )
                    ],
                )
            )

        new_shopping_list_items = [self.repos.group_shopping_list_item.create(item) for item in to_create]

        updated_shopping_list = self.shopping_lists.get_one(list_id)
        if not updated_shopping_list:
            raise UnexpectedNone("Shopping List not found")

        updated_shopping_list_items, deleted_shopping_list_items = self.consolidate_and_save(updated_shopping_list.list_items)  # type: ignore
        updated_shopping_list.list_items = updated_shopping_list_items

        not_found = True
        for refs in updated_shopping_list.recipe_references:
            if refs.recipe_id == recipe_id:
                refs.recipe_quantity += 1
                not_found = False

        if not_found:
            updated_shopping_list.recipe_references.append(
                ShoppingListItemRecipeRef(recipe_id=recipe_id, recipe_quantity=1)  # type: ignore
            )

        updated_shopping_list = self.shopping_lists.update(updated_shopping_list.id, updated_shopping_list)

        """
        There can be overlap between the list item collections, so we de-duplicate the lists.

        First new items are created, then existing items are updated, and finally some items are deleted,
        so we can de-duplicate using this logic
        """
        new_items_map = {list_item.id: list_item for list_item in new_shopping_list_items}
        updated_items_map = {list_item.id: list_item for list_item in updated_shopping_list_items}
        deleted_items_map = {list_item.id: list_item for list_item in deleted_shopping_list_items}

        # if the item was created and then updated, replace the create with the update and remove the update
        for id in list(updated_items_map.keys()):
            if id in new_items_map:
                new_items_map[id] = updated_items_map[id]
                del updated_items_map[id]

        # if the item was updated and then deleted, remove the update
        updated_shopping_list_items = [
            list_item for id, list_item in updated_items_map.items() if id not in deleted_items_map
        ]

        # if the item was created and then deleted, remove it from both lists
        new_shopping_list_items = [list_item for id, list_item in new_items_map.items() if id not in deleted_items_map]
        deleted_shopping_list_items = [
            list_item for id, list_item in deleted_items_map.items() if id not in new_items_map
        ]

        return updated_shopping_list, new_shopping_list_items, updated_shopping_list_items, deleted_shopping_list_items

    def remove_recipe_ingredients_from_list(
        self, list_id: UUID4, recipe_id: UUID4
    ) -> tuple[ShoppingListOut, list[ShoppingListItemOut], list[ShoppingListItemOut]]:
        """
        returns:
            - updated_shopping_list
            - updated_shopping_list_items
            - deleted_shopping_list_items
        """
        shopping_list = self.shopping_lists.get_one(list_id)

        if shopping_list is None:
            raise UnexpectedNone("Shopping list not found, cannot remove recipe ingredients")

        updated_shopping_list_items = []
        deleted_shopping_list_items = []
        for item in shopping_list.list_items:
            found = False

            for ref in item.recipe_references:
                remove_qty: None | float = 0.0

                if ref.recipe_id == recipe_id:
                    self.list_item_refs.delete(ref.id)  # type: ignore
                    item.recipe_references.remove(ref)
                    found = True
                    remove_qty = ref.recipe_quantity
                    break  # only remove one instance of the recipe for each item

            # If the item was found decrement the quantity by the remove_qty
            if found:

                if remove_qty is not None:
                    item.quantity = item.quantity - remove_qty

                if item.quantity <= 0:
                    self.list_items.delete(item.id)
                    deleted_shopping_list_items.append(item)
                else:
                    self.list_items.update(item.id, item)
                    updated_shopping_list_items.append(item)

        # Decrement the list recipe reference count
        for recipe_ref in shopping_list.recipe_references:
            if recipe_ref.recipe_id == recipe_id and recipe_ref.recipe_quantity is not None:
                recipe_ref.recipe_quantity -= 1.0

                if recipe_ref.recipe_quantity <= 0.0:
                    self.list_refs.delete(recipe_ref.id)

                else:
                    self.list_refs.update(recipe_ref.id, ref)
                break

        # Save Changes
        return self.shopping_lists.get_one(shopping_list.id), updated_shopping_list_items, deleted_shopping_list_items  # type: ignore
