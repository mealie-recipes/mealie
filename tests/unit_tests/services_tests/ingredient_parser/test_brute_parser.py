import asyncio

import pytest
from pydantic import UUID4

from mealie.db.db_setup import session_context
from mealie.lang.providers import get_locale_provider
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientFood,
    IngredientUnit,
    ParsedIngredient,
    RecipeIngredient,
)
from mealie.services.parser_services import RegisteredParser, get_parser


def build_parsed_ing(food: str | None, unit: str | None) -> ParsedIngredient:
    ing = RecipeIngredient(unit=None, food=None)
    if food:
        ing.food = CreateIngredientFood(name=food)
    if unit:
        ing.unit = CreateIngredientUnit(name=unit)

    return ParsedIngredient(input=None, ingredient=ing)


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
            id="a stalk bell peppers, cut in pieces",
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
        parser = get_parser(RegisteredParser.brute, unique_local_group_id, session, get_locale_provider())
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
            parser = get_parser(RegisteredParser.brute, unique_local_group_id, session, get_locale_provider())
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
            build_parsed_ing(unit=None, food="n̅ōr̅m̄a̅l̄i̅z̄e̅m̄e̅"),
            None,
            "ñör̃m̈ãl̈ĩz̈ẽm̈ẽ",
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
        parser = get_parser(RegisteredParser.brute, unique_local_group_id, session, get_locale_provider())
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
