from __future__ import annotations

from functools import cached_property
from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood, IngredientFood

from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_recipe_event


class RecipeFoodService(
    CrudHttpMixins[IngredientFood, CreateIngredientFood, CreateIngredientFood],
    UserHttpService[int, IngredientFood],
):
    event_func = create_recipe_event
    _restrict_by_group = False
    _schema = IngredientFood

    @cached_property
    def dal(self):
        return self.db.ingredient_foods

    def populate_item(self, id: int) -> IngredientFood:
        self.item = self.dal.get_one(id)
        return self.item

    def get_all(self) -> list[IngredientFood]:
        return self.dal.get_all()

    def create_one(self, data: CreateIngredientFood) -> IngredientFood:
        return self._create_one(data)

    def update_one(self, data: IngredientFood, item_id: int = None) -> IngredientFood:
        return self._update_one(data, item_id)

    def delete_one(self, id: int = None) -> IngredientFood:
        return self._delete_one(id)
