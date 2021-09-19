from __future__ import annotations

from functools import cached_property

from mealie.schema.recipe.recipe_ingredient import CreateIngredientUnit, IngredientUnit
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_recipe_event


class RecipeUnitService(
    CrudHttpMixins[IngredientUnit, CreateIngredientUnit, CreateIngredientUnit],
    UserHttpService[int, IngredientUnit],
):
    event_func = create_recipe_event
    _restrict_by_group = False
    _schema = IngredientUnit

    @cached_property
    def dal(self):
        return self.db.ingredient_units

    def populate_item(self, id: int) -> IngredientUnit:
        self.item = self.dal.get_one(id)
        return self.item

    def get_all(self) -> list[IngredientUnit]:
        return self.dal.get_all()

    def create_one(self, data: CreateIngredientUnit) -> IngredientUnit:
        return self._create_one(data)

    def update_one(self, data: IngredientUnit, item_id: int = None) -> IngredientUnit:
        return self._update_one(data, item_id)

    def delete_one(self, id: int = None) -> IngredientUnit:
        return self._delete_one(id)
