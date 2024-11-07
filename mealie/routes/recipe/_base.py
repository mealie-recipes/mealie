from functools import cached_property

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from mealie.db.models.household.cookbook import CookBook
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_generic import RepositoryGeneric
from mealie.repos.repository_recipes import RepositoryRecipes
from mealie.routes._base import BaseCrudController
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import (
    CreateRecipe,
)
from mealie.services.recipe.recipe_service import RecipeService


class JSONBytes(JSONResponse):
    """
    JSONBytes overrides the render method to return the bytes instead of a string.
    You can use this when you want to use orjson and bypass the jsonable_encoder
    """

    media_type = "application/json"

    def render(self, content: bytes) -> bytes:
        return content


class FormatResponse(BaseModel):
    jjson: list[str] = Field(..., alias="json")
    zip: list[str]
    jinja2: list[str]


class BaseRecipeController(BaseCrudController):
    @cached_property
    def recipes(self) -> RepositoryRecipes:
        return self.repos.recipes

    @cached_property
    def group_recipes(self) -> RepositoryRecipes:
        return get_repositories(self.session, group_id=self.group_id, household_id=None).recipes

    @cached_property
    def group_cookbooks(self) -> RepositoryGeneric[ReadCookBook, CookBook]:
        return get_repositories(self.session, group_id=self.group_id, household_id=None).cookbooks

    @cached_property
    def service(self) -> RecipeService:
        return RecipeService(self.repos, self.user, self.household, translator=self.translator)

    @cached_property
    def mixins(self):
        return HttpRepo[CreateRecipe, Recipe, Recipe](self.recipes, self.logger)
