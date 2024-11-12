from uuid import UUID

import orjson
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicHouseholdExploreController
from mealie.routes.recipe.recipe_crud_routes import JSONBytes
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.make_dependable import make_dependable
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.recipe.recipe_suggestion import RecipeSuggestionQuery, RecipeSuggestionResponse
from mealie.schema.response.pagination import PaginationBase, PaginationQuery, RecipeSearchQuery

router = APIRouter(prefix="/recipes")


@controller(router)
class PublicRecipesController(BasePublicHouseholdExploreController):
    @property
    def cross_household_cookbooks(self):
        return self.cross_household_repos.cookbooks

    @property
    def cross_household_recipes(self):
        return self.cross_household_repos.recipes

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
        households: list[UUID4 | str] | None = Query(None),
    ) -> PaginationBase[RecipeSummary]:
        cookbook_data: ReadCookBook | None = None
        if search_query.cookbook:
            COOKBOOK_NOT_FOUND_EXCEPTION = HTTPException(404, "cookbook not found")
            if isinstance(search_query.cookbook, UUID):
                cb_match_attr = "id"
            else:
                try:
                    UUID(search_query.cookbook)
                    cb_match_attr = "id"
                except ValueError:
                    cb_match_attr = "slug"
            cookbook_data = self.cross_household_cookbooks.get_one(search_query.cookbook, cb_match_attr)

            if cookbook_data is None or not cookbook_data.public:
                raise COOKBOOK_NOT_FOUND_EXCEPTION
            household = self.repos.households.get_one(cookbook_data.household_id)
            if not household or household.preferences.private_household:
                raise COOKBOOK_NOT_FOUND_EXCEPTION

        public_filter = "(household.preferences.privateHousehold = FALSE AND settings.public = TRUE)"
        if q.query_filter:
            q.query_filter = f"({q.query_filter}) AND {public_filter}"
        else:
            q.query_filter = public_filter

        pagination_response = self.cross_household_recipes.page_all(
            pagination=q,
            cookbook=cookbook_data,
            categories=categories,
            tags=tags,
            tools=tools,
            foods=foods,
            households=households,
            require_all_categories=search_query.require_all_categories,
            require_all_tags=search_query.require_all_tags,
            require_all_tools=search_query.require_all_tools,
            require_all_foods=search_query.require_all_foods,
            search=search_query.search,
        )

        # merge default pagination with the request's query params
        query_params = q.model_dump() | {**request.query_params}
        pagination_response.set_pagination_guides(
            self.get_explore_url_path(router.url_path_for("get_all")),
            {k: v for k, v in query_params.items() if v is not None},
        )

        json_compatible_response = orjson.dumps(pagination_response.model_dump(by_alias=True))

        # Response is returned directly, to avoid validation and improve performance
        return JSONBytes(content=json_compatible_response)

    @router.get("/suggestions", response_model=RecipeSuggestionResponse)
    def suggest_recipes(
        self,
        q: RecipeSuggestionQuery = Depends(make_dependable(RecipeSuggestionQuery)),
        foods: list[UUID4] | None = Query(None),
        tools: list[UUID4] | None = Query(None),
    ) -> RecipeSuggestionResponse:
        public_filter = "(household.preferences.privateHousehold = FALSE AND settings.public = TRUE)"
        if q.query_filter:
            q.query_filter = f"({q.query_filter}) AND {public_filter}"
        else:
            q.query_filter = public_filter

        recipes = self.cross_household_recipes.find_suggested_recipes(q, foods, tools)
        response = RecipeSuggestionResponse(items=recipes)
        json_compatible_response = orjson.dumps(response.model_dump(by_alias=True))

        # Response is returned directly, to avoid validation and improve performance
        return JSONBytes(content=json_compatible_response)

    @router.get("/{recipe_slug}", response_model=Recipe)
    def get_recipe(self, recipe_slug: str) -> Recipe:
        RECIPE_NOT_FOUND_EXCEPTION = HTTPException(404, "recipe not found")
        recipe = self.cross_household_recipes.get_one(recipe_slug)

        if not recipe or not recipe.settings.public:
            raise RECIPE_NOT_FOUND_EXCEPTION
        household = self.repos.households.get_one(recipe.household_id)
        if not household or household.preferences.private_household:
            raise RECIPE_NOT_FOUND_EXCEPTION

        return recipe
