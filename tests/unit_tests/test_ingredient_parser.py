import shutil
from dataclasses import dataclass
from fractions import Fraction

import pytest
from pydantic import UUID4

from mealie.db.db_setup import session_context
from mealie.repos.repository_factory import AllRepositories
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
from mealie.services.parser_services import RegisteredParser, get_parser
from mealie.services.parser_services.crfpp.processor import CRFIngredient, convert_list_to_crf_model
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


@dataclass
class TestIngredient:
    input: str
    quantity: float
    unit: str
    food: str
    comments: str


def crf_exists() -> bool:
    return shutil.which("crf_test") is not None


def build_parsed_ing(food: str | None, unit: str | None) -> ParsedIngredient:
    ing = RecipeIngredient(unit=None, food=None)
    if food:
        ing.food = CreateIngredientFood(name=food)
    if unit:
        ing.unit = CreateIngredientUnit(name=unit)

    return ParsedIngredient(input=None, ingredient=ing)


@pytest.fixture()
def unique_local_group_id(database: AllRepositories) -> UUID4:
    return str(database.groups.create(GroupBase(name=random_string())).id)


@pytest.fixture()
def parsed_ingredient_data(
    database: AllRepositories, unique_local_group_id: UUID4
) -> tuple[list[IngredientFood], list[IngredientUnit]]:
    foods = database.ingredient_foods.create_many(
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
        database.ingredient_foods.create_many(
            [
                SaveIngredientFood(name=f"{random_string()} food", group_id=unique_local_group_id)
                for _ in range(random_int(10, 15))
            ]
        )
    )

    units = database.ingredient_units.create_many(
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
        database.ingredient_foods.create_many(
            [
                SaveIngredientUnit(name=f"{random_string()} unit", group_id=unique_local_group_id)
                for _ in range(random_int(10, 15))
            ]
        )
    )

    return foods, units


# TODO - add more robust test cases
test_ingredients = [
    TestIngredient("½ cup all-purpose flour", 0.5, "cup", "all-purpose flour", ""),
    TestIngredient("1 ½ teaspoons ground black pepper", 1.5, "teaspoon", "black pepper", "ground"),
    TestIngredient("⅔ cup unsweetened flaked coconut", 0.667, "cup", "coconut", "unsweetened flaked"),
    TestIngredient("⅓ cup panko bread crumbs", 0.333, "cup", "panko bread crumbs", ""),
    # Small Fraction Tests - PR #1369
    # Reported error is was for 1/8 - new lowest expected threshold is 1/32
    TestIngredient("1/8 cup all-purpose flour", 0.125, "cup", "all-purpose flour", ""),
    TestIngredient("1/32 cup all-purpose flour", 0.031, "cup", "all-purpose flour", ""),
]


@pytest.mark.skipif(not crf_exists(), reason="CRF++ not installed")
def test_nlp_parser():
    models: list[CRFIngredient] = convert_list_to_crf_model([x.input for x in test_ingredients])

    # Iterate over models and test_ingredients to gather
    for model, test_ingredient in zip(models, test_ingredients):
        assert round(float(sum(Fraction(s) for s in model.qty.split())), 3) == pytest.approx(test_ingredient.quantity)

        assert model.comment == test_ingredient.comments
        assert model.name == test_ingredient.food
        assert model.unit == test_ingredient.unit


def test_brute_parser(unique_user: TestUser):
    # input: (quantity, unit, food, comments)
    expectations = {
        # Dutch
        "1 theelepel koffie": (1, "theelepel", "koffie", ""),
        "3 theelepels koffie": (3, "theelepels", "koffie", ""),
        "1 eetlepel tarwe": (1, "eetlepel", "tarwe", ""),
        "20 eetlepels bloem": (20, "eetlepels", "bloem", ""),
        "1 mespunt kaneel": (1, "mespunt", "kaneel", ""),
        "1 snuf(je) zout": (1, "snuf(je)", "zout", ""),
        "2 tbsp minced cilantro, leaves and stems": (2, "tbsp", "minced cilantro", "leaves and stems"),
        "1 large yellow onion, coarsely chopped": (1, "large", "yellow onion", "coarsely chopped"),
        "1 1/2 tsp garam masala": (1.5, "tsp", "garam masala", ""),
        "2 cups mango chunks, (2 large mangoes) (fresh or frozen)": (
            2,
            "cups",
            "mango chunks, (2 large mangoes)",
            "fresh or frozen",
        ),
    }

    with session_context() as session:
        parser = get_parser(RegisteredParser.brute, unique_user.group_id, session)

        for key, val in expectations.items():
            parsed = parser.parse_one(key)

            assert parsed.ingredient.quantity == val[0]
            assert parsed.ingredient.unit.name == val[1]
            assert parsed.ingredient.food.name == val[2]
            assert parsed.ingredient.note in {val[3], None}


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
        else:
            assert parsed_ingredient.ingredient.food is None or isinstance(
                parsed_ingredient.ingredient.food, CreateIngredientFood
            )

        if expected_unit_name:
            assert parsed_ingredient.ingredient.unit and parsed_ingredient.ingredient.unit.name == expected_unit_name
        else:
            assert parsed_ingredient.ingredient.unit is None

        if expect_unit_match:
            assert isinstance(parsed_ingredient.ingredient.unit, IngredientUnit)
        else:
            assert parsed_ingredient.ingredient.unit is None or isinstance(
                parsed_ingredient.ingredient.unit, CreateIngredientUnit
            )
