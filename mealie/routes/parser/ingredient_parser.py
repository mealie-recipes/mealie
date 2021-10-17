from fastapi import APIRouter, Depends

from mealie.schema.recipe import ParsedIngredient
from mealie.schema.recipe.recipe_ingredient import IngredientRequest, IngredientsRequest
from mealie.services.parser_services import IngredientParserService

public_router = APIRouter(prefix="/parser")


@public_router.post("/ingredients", response_model=list[ParsedIngredient])
def parse_ingredients(
    ingredients: IngredientsRequest,
    p_service: IngredientParserService = Depends(IngredientParserService.private),
):
    p_service.set_parser(parser=ingredients.parser)
    return p_service.parse_ingredients(ingredients.ingredients)


@public_router.post("/ingredient", response_model=ParsedIngredient)
def parse_ingredient(
    ingredient: IngredientRequest,
    p_service: IngredientParserService = Depends(IngredientParserService.private),
):
    p_service.set_parser(parser=ingredient.parser)
    return p_service.parse_ingredient(ingredient.ingredient)
