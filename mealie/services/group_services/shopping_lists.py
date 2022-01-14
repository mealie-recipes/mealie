from pydantic import UUID4

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group import ShoppingListItemCreate, ShoppingListOut


class ShoppingListService:
    def __init__(self, repos: AllRepositories):
        self.repos = repos
        self.repo = repos.group_shopping_lists

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
