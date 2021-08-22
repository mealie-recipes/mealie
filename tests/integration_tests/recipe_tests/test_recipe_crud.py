import json

import pytest
from fastapi.testclient import TestClient
from slugify import slugify
from tests.app_routes import AppRoutes
from tests.utils.recipe_data import RecipeSiteTestCase, get_recipe_test_cases

recipe_test_data = get_recipe_test_cases()


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_create_by_url(api_client: TestClient, api_routes: AppRoutes, recipe_data: RecipeSiteTestCase, user_token):
    api_client.delete(api_routes.recipes_recipe_slug(recipe_data.expected_slug), headers=user_token)

    response = api_client.post(api_routes.recipes_create_url, json={"url": recipe_data.url}, headers=user_token)

    assert response.status_code == 201
    assert json.loads(response.text) == recipe_data.expected_slug


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_read_update(api_client: TestClient, api_routes: AppRoutes, recipe_data: RecipeSiteTestCase, user_token):
    recipe_url = api_routes.recipes_recipe_slug(recipe_data.expected_slug)
    response = api_client.get(recipe_url, headers=user_token)
    assert response.status_code == 200

    recipe = json.loads(response.text)

    test_notes = [
        {"title": "My Test Title1", "text": "My Test Text1"},
        {"title": "My Test Title2", "text": "My Test Text2"},
    ]

    recipe["notes"] = test_notes
    recipe["tools"] = ["one tool", "two tool"]

    test_categories = ["one", "two", "three"]
    recipe["recipeCategory"] = test_categories

    response = api_client.put(recipe_url, json=recipe, headers=user_token)

    assert response.status_code == 200
    assert json.loads(response.text).get("slug") == recipe_data.expected_slug

    response = api_client.get(recipe_url, headers=user_token)
    assert response.status_code == 200
    recipe = json.loads(response.text)

    assert recipe["notes"] == test_notes
    assert recipe["recipeCategory"].sort() == test_categories.sort()


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_rename(api_client: TestClient, api_routes: AppRoutes, recipe_data: RecipeSiteTestCase, user_token):
    recipe_url = api_routes.recipes_recipe_slug(recipe_data.expected_slug)
    response = api_client.get(recipe_url, headers=user_token)
    assert response.status_code == 200

    recipe = json.loads(response.text)
    new_name = recipe.get("name") + "-rename"
    new_slug = slugify(new_name)
    recipe["name"] = new_name

    response = api_client.put(recipe_url, json=recipe, headers=user_token)

    assert response.status_code == 200
    assert json.loads(response.text).get("slug") == new_slug

    recipe_data.expected_slug = new_slug


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_delete(api_client: TestClient, api_routes: AppRoutes, recipe_data: RecipeSiteTestCase, user_token):
    recipe_url = api_routes.recipes_recipe_slug(recipe_data.expected_slug)
    response = api_client.delete(recipe_url, headers=user_token)
    assert response.status_code == 200
