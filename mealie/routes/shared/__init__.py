from functools import cached_property

from pydantic import UUID4

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.recipe import RecipeShareTokenSummary
from mealie.schema.recipe.recipe_share_token import RecipeShareToken, RecipeShareTokenCreate, RecipeShareTokenSave

router = UserAPIRouter(prefix="/shared/recipes", tags=["Shared: Recipes"])


@controller(router)
class RecipeSharedController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.recipe_share_tokens.by_group(self.group_id)

    @cached_property
    def mixins(self):
        return HttpRepo[RecipeShareTokenSave, RecipeShareToken, RecipeShareTokenCreate](self.repo, self.deps.logger)

    @router.get("", response_model=list[RecipeShareTokenSummary])
    def get_all(self, recipe_id: UUID4 = None):
        if recipe_id:
            return self.repo.multi_query({"recipe_id": recipe_id}, override_schema=RecipeShareTokenSummary)
        else:
            return self.repo.get_all(override_schema=RecipeShareTokenSummary)

    @router.post("", response_model=RecipeShareToken, status_code=201)
    def create_one(self, data: RecipeShareTokenCreate) -> RecipeShareToken:
        save_data = RecipeShareTokenSave(**data.dict(), group_id=self.group_id)
        return self.mixins.create_one(save_data)

    @router.get("/{item_id}", response_model=RecipeShareToken)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.delete("/{item_id}")
    def delete_one(self, item_id: UUID4 = None) -> None:
        return self.mixins.delete_one(item_id)
