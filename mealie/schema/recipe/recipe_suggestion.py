from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary, RecipeTool
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientFoodSummary
from mealie.schema.response.pagination import RequestQuery


class RecipeSuggestionQuery(RequestQuery):
    limit: int = 10

    max_missing_foods: int = 5
    max_missing_tools: int = 5

    include_foods_on_hand: bool = True
    include_tools_on_hand: bool = True
    include_substitutions: bool = True


class RecipeSuggestionSubstitutedFood(MealieModel):
    """A food the recipe calls for that the user doesn't have, and the one covering it."""

    food: IngredientFood
    substitute_food: IngredientFoodSummary


class RecipeSuggestionResponseItem(MealieModel):
    recipe: RecipeSummary
    missing_foods: list[IngredientFood]
    substituted_foods: list[RecipeSuggestionSubstitutedFood]
    missing_tools: list[RecipeTool]


class RecipeSuggestionResponse(MealieModel):
    items: list[RecipeSuggestionResponseItem]
