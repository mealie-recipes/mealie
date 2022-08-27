from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicController
from mealie.schema.recipe import Recipe

router = APIRouter(prefix="/explore", tags=["Explore: Recipes"])


@controller(router)
class PublicRecipesController(BasePublicController):
    @router.get("/recipes/{group_id}/{recipe_slug}", response_model=Recipe)
    def get_recipe(self, group_id: UUID4, recipe_slug: str) -> Recipe:
        group = self.repos.groups.get_one(group_id)

        if not group or group.preferences.private_group:
            raise HTTPException(404, "group not found")

        recipe = self.repos.recipes.by_group(group_id).get_one(recipe_slug)

        if not recipe or not recipe.settings.public:
            raise HTTPException(404, "recipe not found")

        return recipe
