import asyncio
import json
from typing import cast
from unittest.mock import MagicMock

import pytest
from pydantic import UUID4

from mealie.db.db_setup import session_context
from mealie.lang.providers import get_locale_provider
from mealie.schema.openai.recipe_ingredient import OpenAIIngredient, OpenAIIngredients
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientFood,
    IngredientUnit,
    ParsedIngredient,
    RecipeIngredient,
    SaveIngredientFood,
)
from mealie.services.openai import OpenAIService
from mealie.services.parser_services import RegisteredParser, get_parser
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_openai_parser(
    unique_local_group_id: UUID4,
    parsed_ingredient_data: tuple[list[IngredientFood], list[IngredientUnit]],  # required so database is populated
    monkeypatch: pytest.MonkeyPatch,
):
    ingredient_count = random_int(10, 20)

    async def mock_get_response(self, prompt: str, message: str, *args, **kwargs) -> OpenAIIngredients | None:
        inputs = json.loads(message)
        data = OpenAIIngredients(
            ingredients=[
                OpenAIIngredient(
                    quantity=random_int(0, 10),
                    unit=random_string(),
                    food=random_string(),
                    note=random_string(),
                )
                for _ in inputs
            ]
        )
        return data

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    with session_context() as session:
        loop = asyncio.get_event_loop()
        parser = get_parser(RegisteredParser.openai, unique_local_group_id, session, get_locale_provider())

        inputs = [random_string() for _ in range(ingredient_count)]
        parsed = loop.run_until_complete(parser.parse(inputs))

        # since OpenAI is mocked, we don't need to validate the data, we just need to make sure parsing works
        # and that it preserves order
        assert len(parsed) == ingredient_count
        for input, output in zip(inputs, parsed, strict=True):
            assert output.input == input


def test_openai_parser_sanitize_output(
    unique_local_group_id: UUID4,
    unique_user: TestUser,
    parsed_ingredient_data: tuple[list[IngredientFood], list[IngredientUnit]],  # required so database is populated
    monkeypatch: pytest.MonkeyPatch,
):
    async def mock_get_raw_response(self, prompt: str, content: list[dict], response_schema) -> MagicMock:
        # Create data with null character in JSON to test preprocessing
        data = OpenAIIngredients(
            ingredients=[
                OpenAIIngredient(
                    quantity=random_int(0, 10),
                    unit="",
                    food="there is a null character here: \x00",
                    note="",
                )
            ]
        )

        # Create a mock raw response which matches the OpenAI chat response format
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = data.model_dump_json()
        return mock_response

    # Mock the raw response here since we want to make sure our service executes processing before loading the model
    monkeypatch.setattr(OpenAIService, "_get_raw_response", mock_get_raw_response)

    with session_context() as session:
        loop = asyncio.get_event_loop()
        parser = get_parser(RegisteredParser.openai, unique_local_group_id, session, get_locale_provider())

        parsed = loop.run_until_complete(parser.parse([""]))
        assert len(parsed) == 1
        parsed_ing = cast(ParsedIngredient, parsed[0])
        assert parsed_ing.ingredient.food
        assert parsed_ing.ingredient.food.name == "there is a null character here: "

        # Make sure we can create a recipe with this ingredient
        assert isinstance(parsed_ing.ingredient.food, CreateIngredientFood)
        food = unique_user.repos.ingredient_foods.create(
            parsed_ing.ingredient.food.cast(SaveIngredientFood, group_id=unique_user.group_id)
        )
        parsed_ing.ingredient.food = food
        unique_user.repos.recipes.create(
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                recipe_ingredient=[parsed_ing.ingredient],
            )
        )


@pytest.mark.parametrize(
    "original_text,quantity,unit,food,note,qty_range,unit_range,food_range,note_range",
    [
        pytest.param(
            "2 cups flour",
            2.0,
            "Cups",
            "flour",
            "",
            (1.0, 1.0),
            (1.0, 1.0),
            (1.0, 1.0),
            (1.0, 1.0),
            id="perfect_match_all_components",
        ),
        pytest.param(
            "2 cups flour",
            3.0,
            "Cups",
            "flour",
            "",
            (0.0, 0.0),
            (1.0, 1.0),
            (1.0, 1.0),
            (1.0, 1.0),
            id="quantity_mismatch",
        ),
        pytest.param(
            "2 cups flour",
            2.0,
            None,
            "flour",
            "",
            (1.0, 1.0),
            (0.4, 0.9),
            (1.0, 1.0),
            (1.0, 1.0),
            id="missing_unit_fallback",
        ),
        pytest.param(
            "2 cups flour",
            2.0,
            "Cups",
            None,
            "",
            (1.0, 1.0),
            (1.0, 1.0),
            (0.4, 0.9),
            (1.0, 1.0),
            id="missing_food_fallback",
        ),
        pytest.param(
            "2 cups flour sifted fresh",
            2.0,
            "Cups",
            "flour",
            "sifted fresh",
            (1.0, 1.0),
            (1.0, 1.0),
            (1.0, 1.0),
            (0.8, 1.0),
            id="note_full_match",
        ),
        pytest.param(
            "2 cups flour sifted",
            2.0,
            "Cups",
            "flour",
            "sifted chopped",
            (1.0, 1.0),
            (1.0, 1.0),
            (1.0, 1.0),
            (0.4, 0.6),
            id="note_partial_match",
        ),
        pytest.param(
            "2 cups flour",
            2.0,
            "Cups",
            "flour",
            "chopped minced",
            (1.0, 1.0),
            (1.0, 1.0),
            (1.0, 1.0),
            (0.0, 0.0),
            id="note_no_match",
        ),
        pytest.param(
            "1.5 tsp salt kosher",
            1.0,
            None,
            None,
            "kosher fine",
            (0.0, 0.0),
            (0.3, 0.7),
            (0.3, 0.7),
            (0.4, 0.6),
            id="multiple_issues",
        ),
        pytest.param(
            "",
            1.0,
            "Cups",
            "flour",
            "fresh",
            (0.0, 0.0),
            (1.0, 1.0),
            (1.0, 1.0),
            (0.0, 0.0),
            id="empty_original_text",
        ),
        pytest.param(
            "salt",
            0.0,
            None,
            "salt",
            "",
            (1.0, 1.0),
            (1.0, 1.0),
            (1.0, 1.0),
            (1.0, 1.0),
            id="zero_quantity_match",
        ),
    ],
)
def test_openai_parser_confidence(
    original_text: str,
    quantity: float | None,
    unit: str | None,
    food: str | None,
    note: str,
    qty_range: tuple[float, float],
    unit_range: tuple[float, float],
    food_range: tuple[float, float],
    note_range: tuple[float, float],
    unique_local_group_id: UUID4,
    parsed_ingredient_data: tuple[list[IngredientFood], list[IngredientUnit]],  # required so database is populated
):
    """Test the _calculate_confidence method of OpenAIParser with various input scenarios."""

    with session_context() as session:
        from mealie.services.parser_services.openai.parser import OpenAIParser

        parser = cast(
            OpenAIParser, get_parser(RegisteredParser.openai, unique_local_group_id, session, get_locale_provider())
        )

        # Create test ingredient
        ingredient = RecipeIngredient(
            original_text=original_text,
            quantity=quantity,
            unit=CreateIngredientUnit(name=unit) if unit else None,
            food=CreateIngredientFood(name=food) if food else None,
            note=note if note else None,
        )

        # Calculate confidence
        confidence = parser._calculate_confidence(original_text, ingredient)

        # All confidence values should be populated (not None) by the method
        assert confidence.quantity is not None, "Quantity confidence should not be None"
        assert confidence.unit is not None, "Unit confidence should not be None"
        assert confidence.food is not None, "Food confidence should not be None"
        assert confidence.comment is not None, "Comment confidence should not be None"
        assert confidence.average is not None, "Average confidence should not be None"

        # Range-based assertions to handle fuzzy matching variability
        qty_min, qty_max = qty_range
        assert qty_min <= confidence.quantity <= qty_max, (
            f"Quantity confidence out of range: expected {qty_range}, got {confidence.quantity}"
        )

        unit_min, unit_max = unit_range
        assert unit_min <= confidence.unit <= unit_max, (
            f"Unit confidence out of range: expected {unit_range}, got {confidence.unit}"
        )

        food_min, food_max = food_range
        assert food_min <= confidence.food <= food_max, (
            f"Food confidence out of range: expected {food_range}, got {confidence.food}"
        )

        note_min, note_max = note_range
        assert note_min <= confidence.comment <= note_max, (
            f"Note confidence out of range: expected {note_range}, got {confidence.comment}"
        )

        # Check that average is calculated correctly
        expected_avg = (confidence.quantity + confidence.unit + confidence.food + confidence.comment) / 4
        assert abs(confidence.average - expected_avg) < 0.001, (
            f"Average confidence mismatch: expected {expected_avg}, got {confidence.average}"
        )
