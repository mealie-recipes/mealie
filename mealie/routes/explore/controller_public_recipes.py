from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicController
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import RecipePagination, RecipePaginationQuery, RecipeSummary

router = APIRouter(prefix="/explore", tags=["Explore: Recipes"])


@controller(router)
class PublicRecipesController(BasePublicController):
    @router.get("/recipes/{group_id}", response_model=RecipePagination)
    def get_group_recipes(
        self,
        group_id: UUID4,
        request: Request,
        q: RecipePaginationQuery = Depends(),
    ) -> list[RecipeSummary]:
        group = self.repos.groups.get_one(group_id)

        if not group or group.preferences.private_group:
            raise HTTPException(404, "group not found")

        # merge default pagination with the request's query params
        query_params = q.dict() | {**request.query_params}

        pagination_response = self.repos.recipes.page_all(
            pagination=q,
            load_food=q.load_food,
            public_only=True,
        )

        pagination_response.set_pagination_guides(
            "/api/explore/recipes",  # TODO - this should be set dynamically
            {k: v for k, v in query_params.items() if v is not None},
        )

        return pagination_response

    @router.get("/recipes/{group_id}/{recipe_slug}", response_model=Recipe)
    def get_recipe(self, group_id: UUID4, recipe_slug: str) -> Recipe:
        group = self.repos.groups.get_one(group_id)

        if not group or group.preferences.private_group:
            raise HTTPException(404, "group not found")

        recipe = self.repos.recipes.by_group(group_id).get_one(recipe_slug)

        if not recipe or not recipe.settings.public:
            raise HTTPException(404, "recipe not found")

        return recipe
