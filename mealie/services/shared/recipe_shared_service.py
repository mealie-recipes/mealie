from functools import cached_property

from pydantic import UUID4

from mealie.schema.recipe.recipe_share_token import (
    RecipeShareToken,
    RecipeShareTokenCreate,
    RecipeShareTokenSave,
    RecipeShareTokenSummary,
)
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_recipe_event


class SharedRecipeService(
    CrudHttpMixins[RecipeShareToken, RecipeShareTokenCreate, RecipeShareTokenCreate],
    UserHttpService[UUID4, RecipeShareToken],
):
    event_func = create_recipe_event
    _restrict_by_group = False
    _schema = RecipeShareToken

    @cached_property
    def repo(self):
        return self.db.recipe_share_tokens

    def populate_item(self, id: UUID4) -> RecipeShareToken:
        self.item = self.repo.get_one(id)
        return self.item

    def get_all(self, recipe_id=None) -> list[RecipeShareTokenSummary]:
        # sourcery skip: assign-if-exp, inline-immediately-returned-variable
        if recipe_id:
            return self.db.recipe_share_tokens.multi_query(
                {"group_id": self.group_id, "recipe_id": recipe_id},
                override_schema=RecipeShareTokenSummary,
            )
        else:
            return self.db.recipe_share_tokens.multi_query(
                {"group_id": self.group_id}, override_schema=RecipeShareTokenSummary
            )

    def create_one(self, data: RecipeShareTokenCreate) -> RecipeShareToken:
        save_data = RecipeShareTokenSave(**data.dict(), group_id=self.group_id)
        return self._create_one(save_data)

    def delete_one(self, item_id: UUID4 = None) -> None:
        item_id = item_id or self.item.id

        return self.repo.delete(item_id)
