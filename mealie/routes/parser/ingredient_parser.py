from fastapi import APIRouter

from mealie.routes._base import BaseUserController, controller
from mealie.schema.recipe import ParsedIngredient
from mealie.schema.recipe.recipe_ingredient import IngredientRequest, IngredientsRequest
from mealie.services.parser_services import get_parser

router = APIRouter(prefix="/parser")


@controller(router)
class IngredientParserController(BaseUserController):
    @router.post("/ingredients", response_model=list[ParsedIngredient])
    def parse_ingredients(self, ingredients: IngredientsRequest):
        parser = get_parser(ingredients.parser)
        return parser.parse(ingredients.ingredients)

    @router.post("/ingredient", response_model=ParsedIngredient)
    def parse_ingredient(self, ingredient: IngredientRequest):
        parser = get_parser(ingredient.parser)
        return parser.parse([ingredient.ingredient])[0]
