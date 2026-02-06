import asyncio
import json
from dataclasses import dataclass
from typing import cast
from unittest.mock import MagicMock

import pytest
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.db.db_setup import session_context
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.openai.recipe_ingredient import OpenAIIngredient, OpenAIIngredients
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientFoodAlias,
    CreateIngredientUnit,
    CreateIngredientUnitAlias,
    IngredientFood,
    IngredientUnit,
    ParsedIngredient,
    RecipeIngredient,
    SaveIngredientFood,
    SaveIngredientUnit,
)
from mealie.schema.user.user import GroupBase
from mealie.services.openai import OpenAIService
from mealie.services.parser_services import RegisteredParser, get_parser
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


@dataclass
class TestIngredient:
    input: str
    quantity: float
    unit: str
    food: str
    comments: str


def build_parsed_ing(food: str | None, unit: str | None) -> ParsedIngredient:
    ing = RecipeIngredient(unit=None, food=None)
    if food:
        ing.food = CreateIngredientFood(name=food)
    if unit:
        ing.unit = CreateIngredientUnit(name=unit)

    return ParsedIngredient(input=None, ingredient=ing)


@pytest.fixture()
def unique_local_group_id(unfiltered_database: AllRepositories) -> UUID4:
    return str(unfiltered_database.groups.create(GroupBase(name=random_string())).id)


@pytest.fixture()
def unique_db(session: Session, unique_local_group_id: str):
    return get_repositories(session, group_id=unique_local_group_id)


@pytest.fixture()
def parsed_ingredient_data(
    unique_db: AllRepositories, unique_local_group_id: UUID4
) -> tuple[list[IngredientFood], list[IngredientUnit]]:
    foods = unique_db.ingredient_foods.create_many(
        [
            SaveIngredientFood(name="potatoes", group_id=unique_local_group_id),
            SaveIngredientFood(name="onion", group_id=unique_local_group_id),
            SaveIngredientFood(name="green onion", group_id=unique_local_group_id),
            SaveIngredientFood(name="frozen pearl onions", group_id=unique_local_group_id),
            SaveIngredientFood(name="bell peppers", group_id=unique_local_group_id),
            SaveIngredientFood(name="red pepper flakes", group_id=unique_local_group_id),
            SaveIngredientFood(name="fresh ginger", group_id=unique_local_group_id),
            SaveIngredientFood(name="ground ginger", group_id=unique_local_group_id),
            SaveIngredientFood(name="ñör̃m̈ãl̈ĩz̈ẽm̈ẽ", group_id=unique_local_group_id),
            SaveIngredientFood(name="PluralFoodTest", plural_name="myfoodisplural", group_id=unique_local_group_id),
            SaveIngredientFood(
                name="IHaveAnAlias",
                group_id=unique_local_group_id,
                aliases=[CreateIngredientFoodAlias(name="thisismyalias")],
            ),
        ]
    )

    foods.extend(
        unique_db.ingredient_foods.create_many(
            [
                SaveIngredientFood(name=f"{random_string()} food", group_id=unique_local_group_id)
                for _ in range(random_int(10, 15))
            ]
        )
    )

    units = unique_db.ingredient_units.create_many(
        [
            SaveIngredientUnit(name="Cups", group_id=unique_local_group_id),
            SaveIngredientUnit(name="Tablespoon", group_id=unique_local_group_id),
            SaveIngredientUnit(name="Teaspoon", group_id=unique_local_group_id),
            SaveIngredientUnit(name="Stalk", group_id=unique_local_group_id),
            SaveIngredientUnit(name="My Very Long Unit Name", abbreviation="mvlun", group_id=unique_local_group_id),
            SaveIngredientUnit(
                name="PluralUnitName",
                plural_name="abc123",
                abbreviation="doremiabc",
                plural_abbreviation="doremi123",
                group_id=unique_local_group_id,
            ),
            SaveIngredientUnit(
                name="IHaveAnAliasToo",
                group_id=unique_local_group_id,
                aliases=[CreateIngredientUnitAlias(name="thisismyalias")],
            ),
        ]
    )

    units.extend(
        unique_db.ingredient_foods.create_many(
            [
                SaveIngredientUnit(name=f"{random_string()} unit", group_id=unique_local_group_id)
                for _ in range(random_int(10, 15))
            ]
        )
    )

    return foods, units


@pytest.mark.parametrize(
    "input, quantity, unit, food, comment",
    [
        pytest.param("1 theelepel koffie", 1, "theelepel", "koffie", "", id="1 theelepel koffie"),
        pytest.param("3 theelepels koffie", 3, "theelepels", "koffie", "", id="3 theelepels koffie"),
        pytest.param("1 eetlepel tarwe", 1, "eetlepel", "tarwe", "", id="1 eetlepel tarwe"),
        pytest.param("20 eetlepels bloem", 20, "eetlepels", "bloem", "", id="20 eetlepels bloem"),
        pytest.param("1 mespunt kaneel", 1, "mespunt", "kaneel", "", id="1 mespunt kaneel"),
        pytest.param("1 snuf(je) zout", 1, "snuf(je)", "zout", "", id="1 snuf(je) zout"),
        pytest.param(
            "2 tbsp minced cilantro, leaves and stems",
            2,
            "tbsp",
            "minced cilantro",
            "leaves and stems",
            id="2 tbsp minced cilantro, leaves and stems",
        ),
        pytest.param(
            "1 large yellow onion, coarsely chopped",
            1,
            "large",
            "yellow onion",
            "coarsely chopped",
            id="1 large yellow onion, coarsely chopped",
        ),
        pytest.param("1 1/2 tsp garam masala", 1.5, "tsp", "garam masala", "", id="1 1/2 tsp garam masala"),
        pytest.param(
            "2 cups mango chunks, (2 large mangoes) (fresh or frozen)",
            2,
            "Cups",
            "mango chunks, (2 large mangoes)",
            "fresh or frozen",
            id="2 cups mango chunks, (2 large mangoes) (fresh or frozen)",
        ),
        pytest.param("stalk onion", 0, "Stalk", "onion", "", id="stalk onion"),
        pytest.param("a stalk bell peppers", 0, "Stalk", "bell peppers", "", id="a stalk bell peppers"),
        pytest.param("a tablespoon unknownFood", 0, "Tablespoon", "unknownFood", "", id="a tablespoon unknownFood"),
        pytest.param(
            "stalk bell peppers, cut in pieces",
            0,
            "Stalk",
            "bell peppers",
            "cut in pieces",
            id="stalk bell peppers, cut in pieces",
        ),
        pytest.param(
            "a stalk bell peppers, cut in pieces",
            0,
            "Stalk",
            "bell peppers",
            "cut in pieces",
            id="stalk bell peppers, cut in pieces",
        ),
        pytest.param("red pepper flakes", 0, "", "red pepper flakes", "", id="red pepper flakes"),
        pytest.param("1 bell peppers", 1, "", "bell peppers", "", id="1 bell peppers"),
        pytest.param("1 stalk bell peppers", 1, "Stalk", "bell peppers", "", id="1 big stalk bell peppers"),
        pytest.param("a big stalk bell peppers", 0, "Stalk", "bell peppers", "", id="a big stalk bell peppers"),
        pytest.param(
            "1 bell peppers, cut in pieces", 1, "", "bell peppers", "cut in pieces", id="1 bell peppers, cut in pieces"
        ),
        pytest.param(
            "bell peppers, cut in pieces", 0, "", "bell peppers", "cut in pieces", id="bell peppers, cut in pieces"
        ),
    ],
)
def test_brute_parser(
    unique_local_group_id: UUID4,
    parsed_ingredient_data: tuple[list[IngredientFood], list[IngredientUnit]],  # required so database is populated
    input: str,
    quantity: int | float,
    unit: str,
    food: str,
    comment: str,
):
    with session_context() as session:
        loop = asyncio.get_event_loop()
        parser = get_parser(RegisteredParser.brute, unique_local_group_id, session)
        parsed = loop.run_until_complete(parser.parse_one(input))
        ing = parsed.ingredient

        if ing.quantity:
            assert ing.quantity == quantity
        else:
            assert not quantity
        if ing.unit:
            assert ing.unit.name == unit
        else:
            assert not unit
        if ing.food:
            assert ing.food.name == food
        else:
            assert not food
        if ing.note:
            assert ing.note == comment
        else:
            assert not comment


@pytest.mark.parametrize(
    "unit, food, expect_unit_match, expect_food_match, expected_avg",
    [
        pytest.param("Cups", "potatoes", True, True, 1.0, id="all matched"),
        pytest.param("Cups", "veryuniquefood", True, False, 0.75, id="unit matched only"),
        pytest.param("veryuniqueunit", "potatoes", False, True, 0.75, id="food matched only"),
        pytest.param("veryuniqueunit", "veryuniquefood", False, False, 0.5, id="neither matched"),
    ],
)
def test_brute_parser_confidence(
    unit: str,
    food: str,
    expect_unit_match: bool,
    expect_food_match: bool,
    expected_avg: float,
    unique_local_group_id: UUID4,
    parsed_ingredient_data: tuple[list[IngredientFood], list[IngredientUnit]],
):
    input_str = f"1 {unit} {food}"

    with session_context() as session:
        original_loop = asyncio.get_event_loop()
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            parser = get_parser(RegisteredParser.brute, unique_local_group_id, session)
            parsed = loop.run_until_complete(parser.parse_one(input_str))
        finally:
            loop.close()
            asyncio.set_event_loop(original_loop)

        conf = parsed.confidence

        assert conf.quantity == 1
        assert conf.comment == 1
        assert conf.unit == (1 if expect_unit_match or not unit else 0)
        assert conf.food == (1 if expect_food_match or not food else 0)
        assert conf.average == expected_avg


@pytest.mark.parametrize(
    "input, expected_unit_name, expected_food_name, expect_unit_match, expect_food_match",
    (
        pytest.param(
            build_parsed_ing(unit="cup", food="potatoes"),
            "Cups",
            "potatoes",
            True,
            True,
            id="basic match",
        ),
        pytest.param(  # this should work in sqlite since "potato" is contained within "potatoes"
            build_parsed_ing(unit="cup", food="potato"),
            "Cups",
            "potatoes",
            True,
            True,
            id="basic fuzzy match",
        ),
        pytest.param(
            build_parsed_ing(unit="tablespoon", food="onion"),
            "Tablespoon",
            "onion",
            True,
            True,
            id="nested match 1",
        ),
        pytest.param(
            build_parsed_ing(unit="teaspoon", food="green onion"),
            "Teaspoon",
            "green onion",
            True,
            True,
            id="nested match 2",
        ),
        pytest.param(
            build_parsed_ing(unit="cup", food="gren onion"),
            "Cups",
            "green onion",
            True,
            True,
            id="nested match 3",
        ),
        pytest.param(
            build_parsed_ing(unit="stalk", food="very unique"),
            "Stalk",
            "very unique",
            True,
            False,
            id="no food match",
        ),
        pytest.param(
            build_parsed_ing(unit="cup", food=None),
            "Cups",
            None,
            True,
            False,
            id="no food input",
        ),
        pytest.param(
            build_parsed_ing(unit="very unique", food="fresh ginger"),
            "very unique",
            "fresh ginger",
            False,
            True,
            id="no unit match",
        ),
        pytest.param(
            build_parsed_ing(unit=None, food="potatoes"),
            None,
            "potatoes",
            False,
            True,
            id="no unit input",
        ),
        pytest.param(
            build_parsed_ing(unit="very unique", food="very unique"),
            "very unique",
            "very unique",
            False,
            False,
            id="no matches",
        ),
        pytest.param(
            build_parsed_ing(unit=None, food=None),
            None,
            None,
            False,
            False,
            id="no input",
        ),
        pytest.param(
            build_parsed_ing(unit="mvlun", food="potatoes"),
            "My Very Long Unit Name",
            "potatoes",
            True,
            True,
            id="unit abbreviation",
        ),
        pytest.param(
            build_parsed_ing(unit=None, food="n̅ōr̅m̄a̅l̄i̅z̄e̅m̄e̅"),
            None,
            "ñör̃m̈ãl̈ĩz̈ẽm̈ẽ",
            False,
            True,
            id="normalization",
        ),
        pytest.param(
            build_parsed_ing(unit=None, food="myfoodisplural"),
            None,
            "PluralFoodTest",
            False,
            True,
            id="plural food name",
        ),
        pytest.param(
            build_parsed_ing(unit="abc123", food=None),
            "PluralUnitName",
            None,
            True,
            False,
            id="plural unit name",
        ),
        pytest.param(
            build_parsed_ing(unit="doremi123", food=None),
            "PluralUnitName",
            None,
            True,
            False,
            id="plural unit abbreviation",
        ),
        pytest.param(
            build_parsed_ing(unit=None, food="thisismyalias"),
            None,
            "IHaveAnAlias",
            False,
            True,
            id="food alias",
        ),
        pytest.param(
            build_parsed_ing(unit="thisismyalias", food=None),
            "IHaveAnAliasToo",
            None,
            True,
            False,
            id="unit alias",
        ),
    ),
)
def test_parser_ingredient_match(
    expected_food_name: str | None,
    expected_unit_name: str | None,
    expect_food_match: bool,
    expect_unit_match: bool,
    input: ParsedIngredient,
    parsed_ingredient_data: tuple[list[IngredientFood], list[IngredientUnit]],  # required so database is populated
    unique_local_group_id: UUID4,
):
    with session_context() as session:
        parser = get_parser(RegisteredParser.brute, unique_local_group_id, session)
        parsed_ingredient = parser.find_ingredient_match(input)

        if expected_food_name:
            assert parsed_ingredient.ingredient.food and parsed_ingredient.ingredient.food.name == expected_food_name
        else:
            assert parsed_ingredient.ingredient.food is None

        if expect_food_match:
            assert isinstance(parsed_ingredient.ingredient.food, IngredientFood)
        elif parsed_ingredient.ingredient.food and parsed_ingredient.ingredient.food.name:
            assert isinstance(parsed_ingredient.ingredient.food, CreateIngredientFood)
        else:
            assert parsed_ingredient.ingredient.food is None

        if expected_unit_name:
            assert parsed_ingredient.ingredient.unit and parsed_ingredient.ingredient.unit.name == expected_unit_name
        else:
            assert parsed_ingredient.ingredient.unit is None

        if expect_unit_match:
            assert isinstance(parsed_ingredient.ingredient.unit, IngredientUnit)
        elif parsed_ingredient.ingredient.unit and parsed_ingredient.ingredient.unit.name:
            assert isinstance(parsed_ingredient.ingredient.unit, CreateIngredientUnit)
        else:
            assert parsed_ingredient.ingredient.unit is None


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
        parser = get_parser(RegisteredParser.openai, unique_local_group_id, session)

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
        parser = get_parser(RegisteredParser.openai, unique_local_group_id, session)

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

        parser = cast(OpenAIParser, get_parser(RegisteredParser.openai, unique_local_group_id, session))

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
