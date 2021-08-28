from fastapi import APIRouter
from pydantic import BaseModel

from mealie.services.scraper.ingredient_nlp.processor import (
    convert_crf_models_to_ingredients,
    convert_list_to_crf_model,
)

public_router = APIRouter()


class IngredientRequest(BaseModel):
    ingredients: list[str]


@public_router.post("/parse/ingredient")
def parse_ingredients(ingredients: IngredientRequest):
    """
    Parse an ingredient string.
    """

    crf_models = convert_list_to_crf_model(ingredients.ingredients)
    ingredients = convert_crf_models_to_ingredients(crf_models)

    return {"ingredient": ingredients}
