import asyncio
from dataclasses import dataclass

import pytest
from pydantic import UUID4

from mealie.db.db_setup import session_context
from mealie.services.parser_services import RegisteredParser, get_parser


@dataclass
class TestIngredient:
    input: str
    quantity: float
    unit: str
    food: str
    comments: str


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
        TestIngredient("2 tablespoons (30ml) vegetable oil ", 2, "tablespoon", "vegetable oil", ""),
        TestIngredient("2 teaspoons salt (to taste) ", 2, "teaspoon", "salt", "to taste"),
        TestIngredient("2 cups chicken broth or beef broth ", 2, "cup", "chicken broth", ""),
        TestIngredient("1/2 cup", 0.5, "cup", "", ""),
    ],
)
def test_nlp_parser(unique_local_group_id: UUID4, test_ingredient: TestIngredient):
    with session_context() as session:
        loop = asyncio.get_event_loop()
        parser = get_parser(RegisteredParser.nlp, unique_local_group_id, session)
        parsed = loop.run_until_complete(parser.parse_one(test_ingredient.input))
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
