from __future__ import annotations

from functools import cached_property

from mealie.schema.recipe.recipe_tool import RecipeTool, RecipeToolCreate
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_recipe_event


class RecipeToolService(
    CrudHttpMixins[RecipeTool, RecipeToolCreate, RecipeToolCreate],
    UserHttpService[int, RecipeTool],
):
    event_func = create_recipe_event
    _restrict_by_group = False
    _schema = RecipeTool

    @cached_property
    def dal(self):
        return self.db.tools

    def populate_item(self, id: int) -> RecipeTool:
        self.item = self.dal.get_one(id)
        return self.item

    def get_all(self) -> list[RecipeTool]:
        return self.dal.get_all()

    def create_one(self, data: RecipeToolCreate) -> RecipeTool:
        return self._create_one(data)

    def update_one(self, data: RecipeTool, item_id: int = None) -> RecipeTool:
        return self._update_one(data, item_id)

    def delete_one(self, id: int = None) -> RecipeTool:
        return self._delete_one(id)
