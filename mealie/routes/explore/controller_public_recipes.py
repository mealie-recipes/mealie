from uuid import UUID

import orjson
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicExploreController
from mealie.routes.recipe.recipe_crud_routes import JSONBytes
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.make_dependable import make_dependable
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.response.pagination import PaginationBase, PaginationQuery, RecipeSearchQuery

router = APIRouter(prefix="/recipes/{group_slug}")


@controller(router)
class PublicRecipesController(BasePublicExploreController):
    @property
    def cookbooks(self):
        return self.repos.cookbooks.by_group(self.group.id)

    @property
    def recipes(self):
        return self.repos.recipes.by_group(self.group.id)

    @router.get("", response_model=PaginationBase[RecipeSummary])
    def get_all(
        self,
        request: Request,
        q: PaginationQuery = Depends(make_dependable(PaginationQuery)),
        search_query: RecipeSearchQuery = Depends(make_dependable(RecipeSearchQuery)),
        categories: list[UUID4 | str] | None = Query(None),
        tags: list[UUID4 | str] | None = Query(None),
        tools: list[UUID4 | str] | None = Query(None),
        foods: list[UUID4 | str] | None = Query(None),
    ) -> PaginationBase[RecipeSummary]:
        cookbook_data: ReadCookBook | None = None
        if search_query.cookbook:
            if isinstance(search_query.cookbook, UUID):
                cb_match_attr = "id"
            else:
                try:
                    UUID(search_query.cookbook)
                    cb_match_attr = "id"
                except ValueError:
                    cb_match_attr = "slug"
            cookbook_data = self.cookbooks.get_one(search_query.cookbook, cb_match_attr)

            if cookbook_data is None or not cookbook_data.public:
                raise HTTPException(status_code=404, detail="cookbook not found")

        public_filter = "settings.public = TRUE"
        if q.query_filter:
            q.query_filter = f"({q.query_filter}) AND {public_filter}"
        else:
            q.query_filter = public_filter

        pagination_response = self.recipes.page_all(
            pagination=q,
            cookbook=cookbook_data,
            categories=categories,
            tags=tags,
            tools=tools,
            foods=foods,
            require_all_categories=search_query.require_all_categories,
            require_all_tags=search_query.require_all_tags,
            require_all_tools=search_query.require_all_tools,
            require_all_foods=search_query.require_all_foods,
            search=search_query.search,
        )

        # merge default pagination with the request's query params
        query_params = q.model_dump() | {**request.query_params}
        pagination_response.set_pagination_guides(
            router.url_path_for("get_all", group_slug=self.group.slug),
            {k: v for k, v in query_params.items() if v is not None},
        )

        json_compatible_response = orjson.dumps(pagination_response.model_dump(by_alias=True))

        # Response is returned directly, to avoid validation and improve performance
        return JSONBytes(content=json_compatible_response)

    @router.get("/{recipe_slug}", response_model=Recipe)
    def get_recipe(self, recipe_slug: str) -> Recipe:
        recipe = self.repos.recipes.by_group(self.group.id).get_one(recipe_slug)

        if not recipe or not recipe.settings.public:
            raise HTTPException(404, "recipe not found")

        return recipe
