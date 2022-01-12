import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_ingredient import RegisteredParser
from tests.unit_tests.test_ingredient_parser import TestIngredient, crf_exists, test_ingredients
from tests.utils.fixture_schemas import TestUser


class Routes:
    ingredient = "/api/parser/ingredient"
    ingredients = "/api/parser/ingredients"


def assert_ingredient(api_response: dict, test_ingredient: TestIngredient):
    assert api_response["ingredient"]["quantity"] == test_ingredient.quantity
    assert api_response["ingredient"]["unit"]["name"] == test_ingredient.unit
    assert api_response["ingredient"]["food"]["name"] == test_ingredient.food
    assert api_response["ingredient"]["note"] == test_ingredient.comments


@pytest.mark.skipif(not crf_exists(), reason="CRF++ not installed")
@pytest.mark.parametrize("test_ingredient", test_ingredients)
def test_recipe_ingredient_parser_nlp(api_client: TestClient, test_ingredient: TestIngredient, unique_user: TestUser):
    payload = {"parser": RegisteredParser.nlp, "ingredient": test_ingredient.input}
    response = api_client.post(Routes.ingredient, json=payload, headers=unique_user.token)
    assert response.status_code == 200
    assert_ingredient(response.json(), test_ingredient)


@pytest.mark.skipif(not crf_exists(), reason="CRF++ not installed")
def test_recipe_ingredients_parser_nlp(api_client: TestClient, unique_user: TestUser):
    payload = {"parser": RegisteredParser.nlp, "ingredients": [x.input for x in test_ingredients]}
    response = api_client.post(Routes.ingredients, json=payload, headers=unique_user.token)
    assert response.status_code == 200

    for api_ingredient, test_ingredient in zip(response.json(), test_ingredients):
        assert_ingredient(api_ingredient, test_ingredient)


@pytest.mark.skip("TODO: Implement")
def test_recipe_ingredient_parser_brute(api_client: TestClient):
    pass


@pytest.mark.skip("TODO: Implement")
def test_recipe_ingredients_parser_brute(api_client: TestClient):
    pass
