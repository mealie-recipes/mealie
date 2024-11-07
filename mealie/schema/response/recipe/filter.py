from pydantic import UUID4

from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.response.pagination import RequestQuery


class RecipeSuggestionQuery(RequestQuery):
    limit: int = 10

    max_missing_foods: int = 5
    max_missing_tools: int = 5

    include_foods_on_hand: bool = True
    include_tools_on_hand: bool = True


class RecipeSuggestionResponseItem(MealieModel):
    recipe: RecipeSummary
    missing_foods: list[UUID4]
    missing_tools: list[UUID4]


class RecipeSuggestionResponse(MealieModel):
    items: list[RecipeSuggestionResponseItem]
