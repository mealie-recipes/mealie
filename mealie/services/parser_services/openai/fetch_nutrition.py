import asyncio
import json
from collections.abc import Awaitable

from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.schema.openai.recipe_nutrition import OpenAINutrition
from mealie.schema.recipe.recipe_nutrition import Nutrition
from mealie.services.openai import OpenAIDataInjection, OpenAIService


class OpenAINutritionParser:
    def __init__(self, group_id: UUID4, session: Session) -> None:
        self.group_id = group_id
        self.session = session

    def _get_prompt(self, service: OpenAIService) -> str:
        data_injections = [
            OpenAIDataInjection(
                description=(
                    "This is the JSON response schema. You must respond in valid JSON that follows this schema. "
                    "Your payload should be as compact as possible, eliminating unncessesary whitespace. Any fields "
                    "with default values which you do not populate should not be in the payload."
                ),
                value=OpenAINutrition,
            ),
        ]

        return service.get_prompt("recipes.fetch-recipe-nutrition", data_injections=data_injections)

    async def fetch(self, ingredients: str) -> Nutrition:
        service = OpenAIService()
        prompt = self._get_prompt(service)

        tasks: list[Awaitable[str | None]] = []

        message = json.dumps(ingredients, separators=(",", ":"))

        tasks.append(service.get_response(prompt, message, force_json_response=True))

        # re-combine chunks into one response
        try:
            responses_json = await asyncio.gather(*tasks)
        except Exception as e:
            raise Exception("Failed to call OpenAI services") from e

        try:
            responses = [
                OpenAINutrition.parse_openai_response(response_json)
                for response_json in responses_json
                if responses_json
            ]
        except Exception as e:
            raise Exception("Failed to parse OpenAI response") from e

        if not responses:
            raise Exception("No response from OpenAI")

        if responses and responses[0].nutrition:
            nutritional_info = responses[0].nutrition
        else:
            nutritional_info = Nutrition()

        return nutritional_info

    @staticmethod
    def _chunk_messages(messages: list[str], n=1) -> list[list[str]]:
        if n < 1:
            n = 1
        return [messages[i : i + n] for i in range(0, len(messages), n)]
