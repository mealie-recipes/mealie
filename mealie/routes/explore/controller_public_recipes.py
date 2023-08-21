from fastapi import APIRouter, HTTPException

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicController
from mealie.schema.recipe import Recipe

router = APIRouter(prefix="/explore", tags=["Explore: Recipes"])


@controller(router)
class PublicRecipesController(BasePublicController):
    @router.get("/recipes/{group_slug}/{recipe_slug}", response_model=Recipe)
    def get_recipe(self, group_slug: str, recipe_slug: str) -> Recipe:
        group = self.repos.groups.get_by_slug_or_id(group_slug)

        if not group or group.preferences.private_group:
            raise HTTPException(404, "group not found")

        recipe = self.repos.recipes.by_group(group.id).get_one(recipe_slug)

        if not recipe or not recipe.settings.public:
            raise HTTPException(404, "recipe not found")

        return recipe
