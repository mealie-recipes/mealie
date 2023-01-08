from typing import cast

from pydantic import UUID4

from mealie.core.exceptions import UnexpectedNone
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group import ShoppingListItemCreate, ShoppingListOut
from mealie.schema.group.group_shopping_list import (
    ShoppingListItemBase,
    ShoppingListItemOut,
    ShoppingListItemRecipeRefCreate,
    ShoppingListItemRecipeRefOut,
    ShoppingListItemsCollectionOut,
    ShoppingListItemUpdateBulk,
)
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit
from mealie.schema.response.pagination import PaginationQuery


class ShoppingListService:
    def __init__(self, repos: AllRepositories):
        self.repos = repos
        self.shopping_lists = repos.group_shopping_lists
        self.list_items = repos.group_shopping_list_item
        self.list_item_refs = repos.group_shopping_list_item_references
        self.list_refs = repos.group_shopping_list_recipe_refs

    @staticmethod
    def can_merge(item1: ShoppingListItemBase, item2: ShoppingListItemBase) -> bool:
        """Check to see if this item can be merged with another item"""

        if any(
            [
                item1.food_id != item2.food_id,
                item1.unit_id != item2.unit_id,
                item1.checked != item2.checked,
            ]
        ):
            return False

        # if foods match, we can merge, otherwise compare the notes
        return bool(item1.food_id) or item1.note == item2.note

    @staticmethod
    def merge_items(
        from_item: ShoppingListItemCreate | ShoppingListItemUpdateBulk,
        to_item: ShoppingListItemOut | ShoppingListItemUpdateBulk,
    ) -> ShoppingListItemUpdateBulk:
        """
        Takes an item and merges it into an already-existing item, then returns a copy

        Attributes of the `to_item` take priority over the `from_item`, except extras with overlapping keys
        """

        to_item.quantity += from_item.quantity
        if to_item.note != from_item.note:
            to_item.note = " | ".join([note for note in [to_item.note, from_item.note] if note])

        if to_item.extras and from_item.extras:
            to_item.extras.update(from_item.extras)

        updated_refs = {ref.recipe_id: ref for ref in from_item.recipe_references}
        for to_ref in to_item.recipe_references:
            if to_ref.recipe_id not in updated_refs:
                updated_refs[to_ref.recipe_id] = to_ref
                continue

            # merge recipe scales
            base_ref = updated_refs[to_ref.recipe_id]

            # if the scale is missing we assume it's 1 for backwards compatibility
            # if the scale is 0 we leave it alone
            if base_ref.recipe_scale is None:
                base_ref.recipe_scale = 1

            if to_ref.recipe_scale is None:
                to_ref.recipe_scale = 1

            base_ref.recipe_scale += to_ref.recipe_scale

        return to_item.cast(ShoppingListItemUpdateBulk, recipe_references=list(updated_refs.values()))

    def bulk_handle_items(
        self,
        *,
        create_items: list[ShoppingListItemCreate] | None = None,
        update_items: list[ShoppingListItemUpdateBulk] | None = None,
        delete_items: list[UUID4] | None = None,
    ) -> ShoppingListItemsCollectionOut:
        """Perform CRUD operations on one or more shopping list items"""

        if create_items is None:
            create_items = []

        if update_items is None:
            update_items = []

        if delete_items is None:
            delete_items = []

        existing_items_map: dict[UUID4, list[ShoppingListItemOut]] = {}

        # compare new items to existing items and update items, and merge them if we can
        create_items_filtered: list[ShoppingListItemCreate] = []
        for create_item in create_items:
            if create_item.shopping_list_id not in existing_items_map:
                query = PaginationQuery(
                    per_page=-1, query_filter=f"shopping_list_id={create_item.shopping_list_id} AND checked=false"
                )
                items_data = self.list_items.page_all(query)
                existing_items_map[create_item.shopping_list_id] = items_data.items

            # merge into existing items
            merged = False
            for existing_item in existing_items_map[create_item.shopping_list_id]:
                if (not self.can_merge(existing_item, create_item)) or (existing_item.id in delete_items):
                    continue

                update_items.append(self.merge_items(create_item, existing_item))
                merged = True
                break

            if merged:
                continue

            # merge into update items
            for update_item in update_items:
                if (
                    (not self.can_merge(create_item, update_item))
                    or update_item.checked
                    or update_item.id in delete_items
                ):
                    continue

                update_item = self.merge_items(create_item, update_item)
                merged = True
                break

            if merged or create_item.quantity < 0:
                continue

            # create the item
            if create_item.checked:
                # checked items should not have recipe references
                create_item.recipe_references = []

            create_items_filtered.append(create_item)

        # create only the filtered subset of items
        create_items = create_items_filtered

        # compare update items with each other and merge them if we can
        update_items_filtered_map: dict[UUID4, ShoppingListItemUpdateBulk] = {}
        for update_item in update_items:
            if update_item.id in delete_items:
                continue

            if update_item.id in update_items_filtered_map:
                # this item id appears more than once in our update list, so we merge them together
                merged_item = self.merge_items(update_item, update_items_filtered_map[update_item.id])
                update_items_filtered_map[merged_item.id] = merged_item
                continue

            if update_item.checked:
                # remove recipe refs if we're checking off an item and don't worry about merging
                update_item.recipe_references = []
                update_items_filtered_map[update_item.id] = update_item
                continue

            # check if there's an update_item that we can merge with
            merged = False
            for filtered_update_item in update_items_filtered_map.values():
                if not self.can_merge(filtered_update_item, update_item):
                    continue

                update_items_filtered_map[filtered_update_item.id] = self.merge_items(update_item, filtered_update_item)
                delete_items.append(update_item.id)
                merged = True
                break

            # if the item was not merged, add it to the filter map
            if not merged:
                update_items_filtered_map[update_item.id] = update_item

            update_items_filtered_map[update_item.id] = update_item

        # filter out items with negative quantities and delete those
        update_items = []
        for update_item in update_items_filtered_map.values():
            if update_item.quantity < 0:
                delete_items.append(update_item.id)

            else:
                update_items.append(update_item)

        created_items = cast(
            list[ShoppingListItemOut],
            self.list_items.create_many(create_items) if create_items else [],  # type: ignore
        )

        updated_items = cast(
            list[ShoppingListItemOut],
            self.list_items.update_many(update_items) if update_items else [],  # type: ignore
        )

        deleted_items = cast(
            list[ShoppingListItemOut],
            self.list_items.delete_many(set(delete_items)) if delete_items else [],  # type: ignore
        )

        # remove recipe references from shopping list if all of its related items have been deleted
        item_recipe_ids_by_list_id: dict[UUID4, set[UUID4]] = {}
        for item in created_items + updated_items + deleted_items:
            item_recipe_ids_by_list_id.setdefault(item.shopping_list_id, set()).update(
                [ref.recipe_id for ref in item.recipe_references]
            )

        list_refs_to_delete: set[UUID4] = set()
        for shopping_list_id in item_recipe_ids_by_list_id:
            shopping_list = cast(ShoppingListOut, self.shopping_lists.get_one(shopping_list_id))
            for list_ref in shopping_list.recipe_references:
                if list_ref.recipe_id not in item_recipe_ids_by_list_id[shopping_list_id]:
                    list_refs_to_delete.add(list_ref.id)

        if list_refs_to_delete:
            self.list_refs.delete_many(list_refs_to_delete)

        return ShoppingListItemsCollectionOut(
            created_items=created_items, updated_items=updated_items, deleted_items=deleted_items
        )

    def get_shopping_list_items_from_recipe(
        self, list_id: UUID4, recipe_id: UUID4, scale: float = 1
    ) -> list[ShoppingListItemCreate]:
        """Generates a list of new list items based on a recipe"""

        recipe = self.repos.recipes.get_one(recipe_id, "id")
        if not recipe:
            raise UnexpectedNone("Recipe not found")

        list_items: list[ShoppingListItemCreate] = []
        for ingredient in recipe.recipe_ingredient:
            if isinstance(ingredient.food, IngredientFood):
                is_food = True
                food_id = ingredient.food.id
                label_id = ingredient.food.label_id

            else:
                is_food = False
                food_id = None
                label_id = None

            if isinstance(ingredient.unit, IngredientUnit):
                unit_id = ingredient.unit.id

            else:
                unit_id = None

            new_item = ShoppingListItemCreate(
                shopping_list_id=list_id,
                is_food=is_food,
                note=ingredient.note,
                quantity=ingredient.quantity * scale if ingredient.quantity else 0,
                food_id=food_id,
                label_id=label_id,
                unit_id=unit_id,
                recipe_references=[
                    ShoppingListItemRecipeRefCreate(
                        recipe_id=recipe.id, recipe_quantity=ingredient.quantity, recipe_scale=scale
                    )
                ],
            )

            # some recipes have the same ingredient multiple times, so we check to see if we can combine them
            merged = False
            for existing_item in list_items:
                if not self.can_merge(existing_item, new_item):
                    continue

                # since this is the same recipe, we combine the quanities, rather than the scales
                # all items will have exactly one recipe reference
                if ingredient.quantity:
                    existing_item.quantity += ingredient.quantity
                    existing_item.recipe_references[0].recipe_quantity += ingredient.quantity  # type: ignore

                # merge notes
                if existing_item.note != new_item.note:
                    existing_item.note = " | ".join([note for note in [existing_item.note, new_item.note] if note])

                merged = True
                break

            if not merged:
                list_items.append(new_item)

        return list_items

    def add_recipe_ingredients_to_list(
        self, list_id: UUID4, recipe_id: UUID4, recipe_increment: float = 1
    ) -> tuple[ShoppingListOut, ShoppingListItemsCollectionOut]:
        """
        Adds a recipe's ingredients to a list

        Returns a tuple of:
        - Updated Shopping List
        - Impacted Shopping List Items
        """

        items_to_create = self.get_shopping_list_items_from_recipe(list_id, recipe_id, recipe_increment)
        item_changes = self.bulk_handle_items(create_items=items_to_create)

        updated_list = cast(ShoppingListOut, self.shopping_lists.get_one(list_id))

        ref_merged = False
        for ref in updated_list.recipe_references:
            if ref.recipe_id != recipe_id:
                continue

            ref.recipe_quantity += recipe_increment
            ref_merged = True
            break

        if not ref_merged:
            updated_list.recipe_references.append(
                ShoppingListItemRecipeRefCreate(recipe_id=recipe_id, recipe_quantity=recipe_increment)  # type: ignore
            )

        updated_list = self.shopping_lists.update(updated_list.id, updated_list)
        return updated_list, item_changes

    def remove_recipe_ingredients_from_list(
        self, list_id: UUID4, recipe_id: UUID4, recipe_decrement: float = 1
    ) -> tuple[ShoppingListOut, ShoppingListItemsCollectionOut]:
        """
        Removes a recipe's ingredients from a list

        Returns a tuple of:
        - Updated Shopping List
        - Impacted Shopping List Items
        """

        shopping_list = self.shopping_lists.get_one(list_id)
        if shopping_list is None:
            raise UnexpectedNone("Shopping list not found, cannot remove recipe ingredients")

        update_items: list[ShoppingListItemUpdateBulk] = []
        delete_items: list[UUID4] = []
        for item in shopping_list.list_items:
            found = False

            refs = cast(list[ShoppingListItemRecipeRefOut], item.recipe_references)
            for ref in refs:
                if ref.recipe_id != recipe_id:
                    continue

                # if the scale is missing we assume it's 1 for backwards compatibility
                # if the scale is 0 we leave it alone
                if ref.recipe_scale is None:
                    ref.recipe_scale = 1

                # recipe quantity should never be None, but we check just in case
                if ref.recipe_quantity is None:
                    ref.recipe_quantity = 0

                # Set Quantity
                if ref.recipe_scale > recipe_decrement:
                    # remove only part of the reference
                    item.quantity -= recipe_decrement * ref.recipe_quantity

                else:
                    # remove everything that's left on the reference
                    item.quantity -= ref.recipe_scale * ref.recipe_quantity

                # Set Reference Scale
                ref.recipe_scale -= recipe_decrement
                if ref.recipe_scale <= 0:
                    item.recipe_references.remove(ref)

                found = True
                break

            if found:
                # only remove a 0 quantity item if we removed its last recipe reference
                if item.quantity < 0 or (item.quantity == 0 and not item.recipe_references):
                    delete_items.append(item.id)

                else:
                    update_items.append(item.cast(ShoppingListItemUpdateBulk))

        changed_items = self.bulk_handle_items(update_items=update_items, delete_items=delete_items)

        # Decrement the list recipe reference count
        for recipe_ref in shopping_list.recipe_references:
            if recipe_ref.recipe_id != recipe_id or recipe_ref.recipe_quantity is None:
                continue

            recipe_ref.recipe_quantity -= recipe_decrement

            if recipe_ref.recipe_quantity <= 0.0:
                self.list_refs.delete(recipe_ref.id)

            else:
                self.list_refs.update(recipe_ref.id, recipe_ref)

            break

        return self.shopping_lists.get_one(shopping_list.id), changed_items  # type: ignore
