from pydantic import UUID4

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

        # If no food or units are present check against the notes field.
        if not all([item1.food, item1.unit, item2.food, item2.unit]):
            return item1.note == item2.note

        # If the items have the same food and unit they can be merged.
        if item1.unit == item2.unit and item1.food == item2.food:
            return True

        # Otherwise Assume They Can't Be Merged
        return False

    def consolidate_list_items(self, item_list: list[ShoppingListItemOut]) -> list[ShoppingListItemOut]:
        """
        itterates through the shopping list provided and returns
        a consolidated list where all items that are matched against multiple values are
        de-duplicated and only the first item is kept where the quantity is updated accoridngly.
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
                        ref.shopping_list_item_id = base_item.id
                        new_refs.append(ref)

                    base_item.recipe_references.extend(new_refs)
                    checked_items.append(inner_index)

            consolidated_list.append(base_item)

        return consolidated_list

    def consolidate_and_save(self, data: list[ShoppingListItemUpdate]):
        # TODO: Convert to update many with single call

        all_updates = []
        keep_ids = []

        for item in self.consolidate_list_items(data):
            updated_data = self.list_items.update(item.id, item)
            all_updates.append(updated_data)
            keep_ids.append(updated_data.id)

        for item in data:
            if item.id not in keep_ids:
                self.list_items.delete(item.id)

        return all_updates

    # =======================================================================
    # Methods

    def add_recipe_ingredients_to_list(self, list_id: UUID4, recipe_id: int) -> ShoppingListOut:
        recipe = self.repos.recipes.get_one(recipe_id, "id")
        to_create = []

        for ingredient in recipe.recipe_ingredient:
            food_id = None
            try:
                food_id = ingredient.food.id
            except AttributeError:
                pass

            label_id = None
            try:
                label_id = ingredient.food.label.id
            except AttributeError:
                pass

            unit_id = None
            try:
                unit_id = ingredient.unit.id
            except AttributeError:
                pass

            to_create.append(
                ShoppingListItemCreate(
                    shopping_list_id=list_id,
                    is_food=not recipe.settings.disable_amount,
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

        for item in to_create:
            self.repos.group_shopping_list_item.create(item)

        updated_list = self.shopping_lists.get_one(list_id)
        updated_list.list_items = self.consolidate_and_save(updated_list.list_items)

        not_found = True
        for refs in updated_list.recipe_references:
            if refs.recipe_id == recipe_id:
                refs.recipe_quantity += 1
                not_found = False

        if not_found:
            updated_list.recipe_references.append(ShoppingListItemRecipeRef(recipe_id=recipe_id, recipe_quantity=1))

        updated_list = self.shopping_lists.update(updated_list.id, updated_list)

        return updated_list

    def remove_recipe_ingredients_from_list(self, list_id: UUID4, recipe_id: int) -> ShoppingListOut:
        shopping_list = self.shopping_lists.get_one(list_id)

        for item in shopping_list.list_items:
            for ref in item.recipe_references:
                found = False
                remove_qty = 0

                if ref.recipe_id == recipe_id:
                    self.list_item_refs.delete(ref.id)
                    found = True
                    remove_qty = ref.recipe_quantity
                    break  # only remove one instance of the recipe for each item

            # If the item was found decrement the quantity by the remove_qty
            if found:
                item.quantity = item.quantity - remove_qty

                if item.quantity <= 0:
                    self.list_items.delete(item.id)
                else:
                    self.list_items.update(item.id, item)

        # Decrament the list recipe reference count
        for ref in shopping_list.recipe_references:
            if ref.recipe_id == recipe_id:
                ref.recipe_quantity -= 1

                if ref.recipe_quantity <= 0:
                    self.list_refs.delete(ref.id)
                break

        # Save Changes
        return self.shopping_lists.get(shopping_list.id)
