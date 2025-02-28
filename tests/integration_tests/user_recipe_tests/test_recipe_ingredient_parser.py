import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_ingredient import RegisteredParser
from tests.unit_tests.test_ingredient_parser import TestIngredient
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser

nlp_test_ingredients = [
    TestIngredient("½ cup all-purpose flour", 0.5, "cup", "all-purpose flour", ""),
    TestIngredient("1 ½ teaspoons ground black pepper", 1.5, "teaspoon", "ground black pepper", ""),
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
]


def assert_ingredient(api_response: dict, test_ingredient: TestIngredient):
    assert api_response["ingredient"]["quantity"] == pytest.approx(test_ingredient.quantity)
    assert api_response["ingredient"]["unit"]["name"] == test_ingredient.unit
    assert api_response["ingredient"]["food"]["name"] == test_ingredient.food
    assert api_response["ingredient"]["note"] == test_ingredient.comments


@pytest.mark.parametrize("test_ingredient", nlp_test_ingredients)
def test_recipe_ingredient_parser_nlp(api_client: TestClient, test_ingredient: TestIngredient, unique_user: TestUser):
    payload = {"parser": RegisteredParser.nlp, "ingredient": test_ingredient.input}
    response = api_client.post(api_routes.parser_ingredient, json=payload, headers=unique_user.token)
    assert response.status_code == 200
    assert_ingredient(response.json(), test_ingredient)


def test_recipe_ingredients_parser_nlp(api_client: TestClient, unique_user: TestUser):
    payload = {"parser": RegisteredParser.nlp, "ingredients": [x.input for x in nlp_test_ingredients]}
    response = api_client.post(api_routes.parser_ingredients, json=payload, headers=unique_user.token)
    assert response.status_code == 200

    for api_ingredient, test_ingredient in zip(response.json(), nlp_test_ingredients, strict=False):
        assert_ingredient(api_ingredient, test_ingredient)


@pytest.mark.skip("TODO: Implement")
def test_recipe_ingredient_parser_brute(api_client: TestClient):
    pass


@pytest.mark.skip("TODO: Implement")
def test_recipe_ingredients_parser_brute(api_client: TestClient):
    pass
