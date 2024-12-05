from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary, RecipeTool
from mealie.schema.recipe.recipe_ingredient import IngredientFood
from mealie.schema.response.pagination import RequestQuery


class RecipeSuggestionQuery(RequestQuery):
    limit: int = 10

    max_missing_foods: int = 5
    max_missing_tools: int = 5

    include_foods_on_hand: bool = True
    include_tools_on_hand: bool = True


class RecipeSuggestionResponseItem(MealieModel):
    recipe: RecipeSummary
    missing_foods: list[IngredientFood]
    missing_tools: list[RecipeTool]


class RecipeSuggestionResponse(MealieModel):
    items: list[RecipeSuggestionResponseItem]
