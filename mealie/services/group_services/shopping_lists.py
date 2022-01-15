from pydantic import UUID4

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group import ShoppingListItemCreate, ShoppingListOut
from mealie.schema.group.group_shopping_list import ShoppingListItemOut


class ShoppingListService:
    def __init__(self, repos: AllRepositories):
        self.repos = repos
        self.repo = repos.group_shopping_lists

    def consolidate_list_items(self, item_list: list[ShoppingListItemOut]) -> list[ShoppingListItemOut]:
        """
        itterates through the shopping list provided and returns
        a consolidated list where all items that are matched against multiple values are
        de-duplicated and only the first item is kept where the quantity is updated accoridngly.
        """

        def can_merge(item1: ShoppingListItemOut, item2: ShoppingListItemOut) -> bool:
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

        consolidated_list: list[ShoppingListItemOut] = []
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

    # =======================================================================
    # Methods

    def add_recipe_ingredients_to_list(self, list_id: UUID4, recipe_id: int) -> ShoppingListOut:
        recipe = self.repos.recipes.get_one(recipe_id, "id")
        shopping_list = self.repo.get_one(list_id)

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
                )
            )

        shopping_list.list_items.extend(to_create)
        return self.repo.update(shopping_list.id, shopping_list)

    def remove_recipe_ingredients_from_list(self, list_id: UUID4, recipe_id: int) -> ShoppingListOut:
        shopping_list = self.repo.get_one(list_id)
        shopping_list.list_items = [x for x in shopping_list.list_items if x.recipe_id != recipe_id]
        return self.repo.update(shopping_list.id, shopping_list)
