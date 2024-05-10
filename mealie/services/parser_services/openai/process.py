import json

from pydantic import BaseModel
from mealie.services.openai import OpenAIDataInjection, OpenAIService


class OpenAIIngredient(BaseModel):
    input: str
    confidence: float | None = None

    quantity: float | None = 0
    unit: str | None = None
    food: str | None = None
    note: str | None = None


class OpenAIIngredients(BaseModel):
    ingredients: list[OpenAIIngredient] = []


async def parse(ingredients: list[str]) -> OpenAIIngredients:
    service = OpenAIService()
    data_injections = [
        OpenAIDataInjection(
            description=(
                "This is the JSON response schema. You must respond in valid JSON that follows this schema. "
                "Your payload should be as compact as possible, eliminating unncessesary whitespace. Any fields "
                "with default values which you do not populate should not be in the payload."
            ),
            value=OpenAIIngredients,
        ),
    ]

    prompt = service.get_prompt("recipes.parse-recipe-ingredients", data_injections=data_injections)
    response = await service.get_response(
        prompt, json.dumps(ingredients, separators=(",", ":")), force_json_response=True
    )
    if not response:
        raise Exception("No response from OpenAI")

    return OpenAIIngredients.model_validate_json(response)
