import orjson
from fastapi import APIRouter, Depends, HTTPException, Request

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicController
from mealie.routes.recipe.recipe_crud_routes import JSONBytes
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.make_dependable import make_dependable
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.response.pagination import PaginationBase, PaginationQuery, RecipeSearchQuery

router = APIRouter(prefix="/explore", tags=["Explore: Recipes"])


@controller(router)
class PublicRecipesController(BasePublicController):
    @router.get("/recipes/{group_slug}", response_model=PaginationBase[RecipeSummary])
    def get_all(
        self,
        group_slug: str,
        request: Request,
        q: PaginationQuery = Depends(make_dependable(PaginationQuery)),
        search_query: RecipeSearchQuery = Depends(make_dependable(RecipeSearchQuery)),
    ) -> PaginationBase[RecipeSummary]:
        group = self.repos.groups.get_by_slug_or_id(group_slug)

        if not group or group.preferences.private_group:
            raise HTTPException(404, "group not found")

        cookbook_data: ReadCookBook | None = None
        if search_query.cookbook:
            cookbooks_repo = self.repos.recipes.by_group(group.id)
            cb_match_attr = "slug" if isinstance(search_query.cookbook, str) else "id"
            cookbook_data = cookbooks_repo.get_one(search_query.cookbook, cb_match_attr)

            if cookbook_data is None:
                raise HTTPException(status_code=404, detail="cookbook not found")

        public_filter = "settings.public = TRUE"
        if q.query_filter:
            q.query_filter = f"({q.query_filter}) AND {public_filter}"
        else:
            q.query_filter = public_filter

        recipes_repo = self.repos.recipes.by_group(group.id)
        pagination_response = recipes_repo.page_all(
            pagination=q,
            cookbook=cookbook_data,
            require_all_categories=search_query.require_all_categories,
            require_all_tags=search_query.require_all_tags,
            require_all_tools=search_query.require_all_tools,
            require_all_foods=search_query.require_all_foods,
            search=search_query.search,
        )

        # merge default pagination with the request's query params
        query_params = q.dict() | {**request.query_params}
        pagination_response.set_pagination_guides(
            router.url_path_for("get_all", group_slug=group_slug),
            {k: v for k, v in query_params.items() if v is not None},
        )

        json_compatible_response = orjson.dumps(pagination_response.dict(by_alias=True))

        # Response is returned directly, to avoid validation and improve performance
        return JSONBytes(content=json_compatible_response)

    @router.get("/recipes/{group_slug}/{recipe_slug}", response_model=Recipe)
    def get_recipe(self, group_slug: str, recipe_slug: str) -> Recipe:
        group = self.repos.groups.get_by_slug_or_id(group_slug)

        if not group or group.preferences.private_group:
            raise HTTPException(404, "group not found")

        recipe = self.repos.recipes.by_group(group.id).get_one(recipe_slug)

        if not recipe or not recipe.settings.public:
            raise HTTPException(404, "recipe not found")

        return recipe
