import asyncio
import json

from rapidfuzz import fuzz

from mealie.schema.openai.recipe_ingredient import OpenAIIngredient, OpenAIIngredients
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientConfidence,
    ParsedIngredient,
    RecipeIngredient,
)
from mealie.services.openai import OpenAIDataInjection, OpenAIService

from .._base import ABCIngredientParser
from ..parser_utils import extract_quantity_from_string


class OpenAIParser(ABCIngredientParser):
    def _calculate_qty_conf(self, original_text: str, parsed_qty: float | None) -> float:
        """Compares the extracted quantity to a brute-force parsed quantity."""

        expected_qty, _ = extract_quantity_from_string(original_text)
        parsed_qty = parsed_qty or 0
        if parsed_qty == expected_qty:
            return 1
        else:
            return 0

    def _calculate_note_conf(self, original_text: str, note: str | None) -> float:
        """
        Calculate confidence based on how many words in the note are found in the original text.
        Uses alphanumeric filtering and lowercasing to improve matching.
        """

        if not note:
            return 1

        note_words: list[str] = []
        for word in note.strip().lower().split():
            clean_word = "".join(filter(str.isalnum, word))
            if clean_word:
                note_words.append(clean_word)

        if not note_words:
            return 1

        original_words: list[str] = []
        for word in original_text.strip().lower().split():
            clean_word = "".join(filter(str.isalnum, word))
            if clean_word:
                original_words.append(clean_word)

        note_conf_sum = sum(1 for word in note_words if word in original_words)
        return note_conf_sum / len(note_words)

    def _calculate_overall_confidence(self, original_text: str, ing_text: str) -> float:
        """
        Calculate overall confidence based on fuzzy matching between the original text and the ingredient text.
        Uses token sort ratio to account for word order variations.
        """

        ratio = fuzz.token_sort_ratio(original_text, ing_text)
        return ratio / 100.0

    def _calculate_confidence(self, original_text: str, ing: RecipeIngredient) -> IngredientConfidence:
        qty_conf = self._calculate_qty_conf(original_text, ing.quantity)
        note_conf = self._calculate_note_conf(original_text, ing.note)

        # Not all ingredients will have a food and/or unit,
        # so if either is missing we fall back to overall confidence.
        overall_confidence = self._calculate_overall_confidence(original_text, ing.display)
        if ing.food:
            food_conf = 1.0
        else:
            food_conf = overall_confidence

        if ing.unit:
            unit_conf = 1.0
        else:
            unit_conf = overall_confidence

        return IngredientConfidence(
            average=(qty_conf + unit_conf + food_conf + note_conf) / 4,
            quantity=qty_conf,
            unit=unit_conf,
            food=food_conf,
            comment=note_conf,
        )

    def _convert_ingredient(self, original_text: str, openai_ing: OpenAIIngredient) -> ParsedIngredient:
        ingredient = RecipeIngredient(
            original_text=original_text,
            quantity=openai_ing.quantity,
            unit=CreateIngredientUnit(name=openai_ing.unit) if openai_ing.unit else None,
            food=CreateIngredientFood(name=openai_ing.food) if openai_ing.food else None,
            note=openai_ing.note,
        )

        parsed_ingredient = ParsedIngredient(
            input=original_text,
            confidence=self._calculate_confidence(original_text, ingredient),
            ingredient=ingredient,
        )

        return self.find_ingredient_match(parsed_ingredient)

    def _get_prompt(self, service: OpenAIService) -> str:
        if service.send_db_data and self.data_matcher.units_by_alias:
            data_injections = [
                OpenAIDataInjection(
                    description=(
                        "Below is a list of units found in the units database. While parsing, you should "
                        "reference this list when determining which part of the input is the unit. You may "
                        "find a unit in the input that does not exist in this list. This should not prevent "
                        "you from parsing that text as a unit."
                    ),
                    value=list(set(self.data_matcher.units_by_alias)),
                ),
            ]

        else:
            data_injections = None

        return service.get_prompt("recipes.parse-recipe-ingredients", data_injections=data_injections)

    @staticmethod
    def _chunk_messages(messages: list[str], n=1) -> list[list[str]]:
        if n < 1:
            n = 1
        return [messages[i : i + n] for i in range(0, len(messages), n)]

    async def _parse(self, ingredients: list[str]) -> OpenAIIngredients:
        service = OpenAIService()
        prompt = self._get_prompt(service)

        # chunk ingredients and send each chunk to its own worker
        ingredient_chunks = self._chunk_messages(ingredients, n=service.workers)
        tasks = [
            service.get_response(prompt, json.dumps(chunk, separators=(",", ":")), response_schema=OpenAIIngredients)
            for chunk in ingredient_chunks
        ]

        # re-combine chunks into one response
        try:
            unfiltered_responses = await asyncio.gather(*tasks)
        except Exception as e:
            raise Exception("Failed to call OpenAI services") from e

        responses = [response for response in unfiltered_responses if response]
        if not responses:
            raise Exception("No response from OpenAI")

        return OpenAIIngredients(
            ingredients=[ingredient for response in responses for ingredient in response.ingredients]
        )

    async def parse_one(self, ingredient_string: str) -> ParsedIngredient:
        items = await self.parse([ingredient_string])
        return items[0]

    async def parse(self, ingredients: list[str]) -> list[ParsedIngredient]:
        response = await self._parse(ingredients)
        if len(response.ingredients) != len(ingredients):
            raise ValueError(
                "OpenAI returned an unexpected number of ingredients. "
                f"Expected {len(ingredients)}, got {len(response.ingredients)}"
            )

        return [
            self._convert_ingredient(original_text, ing)
            for original_text, ing in zip(ingredients, response.ingredients, strict=True)
        ]
