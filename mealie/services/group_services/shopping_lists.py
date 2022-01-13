from functools import cached_property

from pydantic import UUID4

from mealie.schema.group import ShoppingListCreate, ShoppingListOut, ShoppingListSummary
from mealie.schema.group.group_shopping_list import ShoppingListItemCreate
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_group_event


class ShoppingListService(
    CrudHttpMixins[ShoppingListOut, ShoppingListCreate, ShoppingListCreate],
    UserHttpService[int, ShoppingListOut],
):
    event_func = create_group_event
    _restrict_by_group = True
    _schema = ShoppingListSummary

    @cached_property
    def repo(self):
        return self.db.group_shopping_lists

    def add_recipe_ingredients_to_list(self, list_id: UUID4, recipe_id: int) -> ShoppingListOut:
        recipe = self.db.recipes.get_one(recipe_id, "id")
        shopping_list = self.repo.get_one(list_id)

        to_create = []

        for ingredient in recipe.recipe_ingredient:
            food_id = None
            try:
                food_id = ingredient.food.id
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
                    is_food=True,
                    food_id=food_id,
                    unit_id=unit_id,
                    quantity=ingredient.quantity,
                    note=ingredient.note,
                    recipe_id=recipe_id,
                )
            )

        shopping_list.list_items.extend(to_create)
        return self.repo.update(shopping_list.id, shopping_list)

    def remove_recipe_ingredients_from_list(self, list_id: UUID4, recipe_id: int) -> ShoppingListOut:
        shopping_list = self.repo.get_one(list_id)
        shopping_list.list_items = [x for x in shopping_list.list_items if x.recipe_id != recipe_id]
        return self.repo.update(shopping_list.id, shopping_list)
