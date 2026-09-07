import asyncio
import re
from dataclasses import dataclass
from typing import cast

import pytest
from pydantic import UUID4
from rapidfuzz import fuzz
from text_unidecode import unidecode

from mealie.db.db_setup import session_context
from mealie.lang.providers import get_locale_provider
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    CreateIngredientUnit,
    IngredientFood,
    IngredientUnit,
    RecipeIngredient,
)
from mealie.services.parser_services import RegisteredParser, get_parser
from mealie.services.parser_services.ingredient_parser import NLPParser


@dataclass
class TestIngredient:
    input: str
    quantity: float
    unit: str
    food: str
    comments: str


def normalize(val: str) -> str:
    val = unidecode(val).lower().strip()
    val = re.sub(r"[^a-z0-9\s]", "", val)
    return val


@pytest.mark.parametrize(
    "test_ingredient",
    [
        TestIngredient("½ cup all-purpose flour", 0.5, "cup", "all-purpose flour", ""),
        TestIngredient("1 ½ teaspoons ground black pepper", 1.5, "teaspoon", "black pepper", "ground"),
        TestIngredient("⅔ cup unsweetened flaked coconut", 0.667, "cup", "unsweetened flaked coconut", ""),
        TestIngredient("⅓ cup panko bread crumbs", 0.333, "cup", "panko bread crumbs", ""),
        TestIngredient("1/8 cup all-purpose flour", 0.125, "cup", "all-purpose flour", ""),
        TestIngredient("1/32 cup all-purpose flour", 0.031, "cup", "all-purpose flour", ""),
        TestIngredient("1 1/2 cups chopped onion ", 1.5, "cup", "onion", "chopped"),
        TestIngredient(
            "2 pounds russet potatoes, peeled, and cut into 3/4-inch cubes  ",
            2,
            "pound",
            "russet potatoes",
            "peeled, and cut into 3/4 inch cubes",
        ),
        TestIngredient("2 teaspoons salt (to taste) ", 2, "teaspoon", "salt", "to taste"),
        TestIngredient("1/2 cup", 0.5, "cup", "", ""),
    ],
)
def test_nlp_parser(unique_local_group_id: UUID4, test_ingredient: TestIngredient):
    with session_context() as session:
        parser = get_parser(RegisteredParser.nlp, unique_local_group_id, session, get_locale_provider())
        parsed = asyncio.run(parser.parse_one(test_ingredient.input))
        ing = parsed.ingredient

        assert ing.quantity == pytest.approx(test_ingredient.quantity)
        if ing.unit:
            assert ing.unit.name == test_ingredient.unit
        else:
            assert not test_ingredient.unit
        if ing.food:
            assert ing.food.name == test_ingredient.food
        else:
            assert not test_ingredient.food
        if ing.note:
            assert ing.note == test_ingredient.comments
        else:
            assert not test_ingredient.comments


@pytest.mark.parametrize(
    ("source_str", "expected_str"),
    [
        (
            "2 teaspoon chopped fresh or dried rosemary",
            "2 teaspoon fresh rosemary or dried rosemary chopped",
        ),
        (
            "153 grams 00 flour (1 cup plus 1 tablespoon)",
            "153 gram 00 flour or 1 cup and 1 tablespoon",
        ),
        (
            "153 grams all-purpose flour (1 cup plus 1 tablespoon and 2 teaspoons)",
            "153 gram all-purpose flour or 1 cup plus 1 tablespoon and 2 teaspoons",
        ),
        (
            "2 cups chicken broth or beef broth",
            "2 cup chicken broth or beef broth",
        ),
        (
            "2 tablespoons (30ml) vegetable oil",
            "2 tablespoon vegetable oil or 30 milliliter",
        ),
        (
            "1 cup fresh basil or 2 tablespoons dried basil",
            "1 cup fresh basil or 2 tablespoons dried basil",
        ),
    ],
)
@pytest.mark.asyncio
async def test_nlp_parser_keeps_all_text(unique_local_group_id: UUID4, source_str: str, expected_str: str):
    with session_context() as session:
        parser = get_parser(RegisteredParser.nlp, unique_local_group_id, session, get_locale_provider())
        parsed = await parser.parse_one(source_str)

    ing = parsed.ingredient

    # alternatives ("or dried rosemary") are substitutions now rather than note text, so both
    # halves have to be read back to know nothing was dropped. this group has no foods, so every
    # alternative falls back to its own text instead of resolving to a food id
    parsed_text = " or ".join([ing.display, *(sub.note for sub in ing.substitutions if sub.note)])

    # The parser behavior may change slightly, so we check that it's pretty close rather than exact.
    # token_sort_ratio rather than ratio, since moving the alternatives out of the note reorders
    # the same words and this test is about none of them going missing
    score = fuzz.token_sort_ratio(parsed_text, expected_str)
    assert score >= 90, f"'{parsed_text}' does not sufficiently match expected '{expected_str}'"


def test_nlp_parser_converts_extra_ingredients(
    unique_local_group_id: UUID4,
    parsed_ingredient_data: tuple[list[IngredientFood], list[IngredientUnit]],  # required so database is populated
):
    """
    An alternative naming a known food becomes a food substitution; anything else keeps its text,
    so an amount the substitution cannot carry is not silently dropped.
    """

    with session_context() as session:
        parser = cast(
            NLPParser, get_parser(RegisteredParser.nlp, unique_local_group_id, session, get_locale_provider())
        )

        substitutions = parser._convert_extra_ingredients(
            [
                RecipeIngredient(food=CreateIngredientFood(name="onion")),
                RecipeIngredient(food=CreateIngredientFood(name="unobtainium extract")),
                RecipeIngredient(
                    quantity=2,
                    unit=CreateIngredientUnit(name="cups"),
                    food=CreateIngredientFood(name="onion"),
                ),
            ]
        )

        onion = parser.data_matcher.find_food_match("onion")
        assert onion

    assert len(substitutions) == 3

    assert substitutions[0].substitute_food_id == onion.id
    assert substitutions[0].note is None

    assert substitutions[1].substitute_food_id is None
    assert substitutions[1].note == "unobtainium extract"

    # the amount has nowhere to live on a substitution, so the whole thing stays as text
    assert substitutions[2].substitute_food_id is None
    assert substitutions[2].note and "onion" in substitutions[2].note
