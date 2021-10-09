from fastapi import APIRouter, Depends
from pydantic import BaseModel

from mealie.schema.recipe import RecipeIngredient
from mealie.services.parser_services import IngredientParserService

public_router = APIRouter(prefix="/parser")


class IngredientsRequest(BaseModel):
    ingredients: list[str]


class IngredientRequest(BaseModel):
    ingredient: str


@public_router.post("/ingredients", response_model=list[RecipeIngredient])
def parse_ingredients(
    ingredients: IngredientsRequest,
    p_service: IngredientParserService = Depends(IngredientParserService.private),
):
    return {"ingredients": p_service.parse_ingredients(ingredients.ingredients)}


@public_router.post("/ingredient")
def parse_ingredient(
    ingredient: IngredientRequest,
    p_service: IngredientParserService = Depends(IngredientParserService.private),
):
    return {"ingredient": p_service.parse_ingredient(ingredient.ingredient)}
