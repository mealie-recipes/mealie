from __future__ import annotations

from functools import cached_property
from uuid import UUID

from mealie.core.root_logger import get_logger
from mealie.schema.group import (
    ShoppingListCreate,
    ShoppingListOut,
    ShoppingListSave,
    ShoppingListSummary,
    ShoppingListUpdate,
)
from mealie.schema.group.group_shopping_list import ShoppingListItemCreate
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_group_event

logger = get_logger(module=__name__)


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

    def populate_item(self, id: int) -> ShoppingListOut:
        self.item = self.repo.get_one(id)
        return self.item

    def get_all(self) -> list[ShoppingListSummary]:
        return self.repo.get(self.group_id, match_key="group_id", limit=9999)

    def create_one(self, data: ShoppingListCreate) -> ShoppingListOut:
        data = self.cast(data, ShoppingListSave)
        return self._create_one(data)

    def update_one(self, data: ShoppingListUpdate, item_id: int = None) -> ShoppingListOut:
        return self._update_one(data, item_id)

    def delete_one(self, id: int = None) -> ShoppingListOut:
        return self._delete_one(id)

    def add_recipe_ingredients_to_list(self, list_id: UUID, recipe_id: int) -> ShoppingListOut:
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
                unit_id = ingredient.food.id
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
                )
            )

        shopping_list.list_items.extend(to_create)
        return self.update_one(shopping_list, shopping_list.id)
