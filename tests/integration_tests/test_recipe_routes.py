import json

import pytest
from fastapi.testclient import TestClient
from slugify import slugify
from tests.app_routes import AppRoutes
from tests.utils.recipe_data import RecipeTestData, build_recipe_store

recipe_test_data = build_recipe_store()


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_create_by_url(api_client: TestClient, api_routes: AppRoutes, recipe_data: RecipeTestData, token):

    api_client.delete(api_routes.recipes_recipe_slug(recipe_data.expected_slug), headers=token)
    response = api_client.post(api_routes.recipes_create_url, json={"url": recipe_data.url}, headers=token)
    assert response.status_code == 201
    assert json.loads(response.text) == recipe_data.expected_slug


def test_create_by_json(api_client: TestClient, api_routes: AppRoutes, token, raw_recipe):
    recipe_url = api_routes.recipes_recipe_slug("banana-bread")
    api_client.delete(recipe_url, headers=token)
    response = api_client.post(api_routes.recipes_create, json=raw_recipe, headers=token)

    assert response.status_code == 201
    assert json.loads(response.text) == "banana-bread"


def test_create_no_image(api_client: TestClient, api_routes: AppRoutes, token, raw_recipe_no_image):
    response = api_client.post(api_routes.recipes_create, json=raw_recipe_no_image, headers=token)

    assert response.status_code == 201
    assert json.loads(response.text) == "banana-bread-no-image"


def test_read_all_post(api_client: TestClient, api_routes: AppRoutes):
    response = api_client.post(api_routes.recipes, json={"properties": ["slug", "description", "rating"]})
    assert response.status_code == 200


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_read_update(api_client: TestClient, api_routes: AppRoutes, recipe_data, token):
    recipe_url = api_routes.recipes_recipe_slug(recipe_data.expected_slug)
    response = api_client.get(recipe_url, headers=token)
    assert response.status_code == 200

    recipe = json.loads(response.content)

    test_notes = [
        {"title": "My Test Title1", "text": "My Test Text1"},
        {"title": "My Test Title2", "text": "My Test Text2"},
    ]
    recipe["notes"] = test_notes
    recipe["tools"] = ["one tool", "two tool"]

    test_categories = ["one", "two", "three"]
    recipe["recipeCategory"] = test_categories

    response = api_client.put(recipe_url, json=recipe, headers=token)

    assert response.status_code == 200
    assert json.loads(response.text).get("slug") == recipe_data.expected_slug

    response = api_client.get(recipe_url)

    recipe = json.loads(response.content)

    assert recipe["notes"] == test_notes
    assert recipe["recipeCategory"].sort() == test_categories.sort()


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_rename(api_client: TestClient, api_routes: AppRoutes, recipe_data, token):
    recipe_url = api_routes.recipes_recipe_slug(recipe_data.expected_slug)
    response = api_client.get(recipe_url, headers=token)
    assert response.status_code == 200

    recipe = json.loads(response.text)
    new_name = recipe.get("name") + "-rename"
    new_slug = slugify(new_name)
    recipe["name"] = new_name

    response = api_client.put(recipe_url, json=recipe, headers=token)

    assert response.status_code == 200
    assert json.loads(response.text).get("slug") == new_slug

    recipe_data.expected_slug = new_slug


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_delete(api_client: TestClient, api_routes: AppRoutes, recipe_data, token):
    recipe_url = api_routes.recipes_recipe_slug(recipe_data.expected_slug)
    response = api_client.delete(recipe_url, headers=token)
    assert response.status_code == 200
