import json

import pytest
from slugify import slugify
from tests.test_routes.utils.routes_data import (RecipeTestData,
                                                 raw_recipe_dict,
                                                 recipe_test_data)


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_create_by_url(api_client, recipe_data: RecipeTestData):
    response = api_client.post("/api/recipe/create-url/", json={"url": recipe_data.url})
    assert response.status_code == 201
    assert json.loads(response.text) == recipe_data.expected_slug


def test_create_by_json(api_client):
    response = api_client.post("/api/recipe/create/", json=raw_recipe_dict)

    assert response.status_code == 200
    assert json.loads(response.text) == "banana-bread"


def test_read_all_post(api_client):
    response = api_client.post(
        "/api/all-recipes/", json={"properties": ["slug", "description", "rating"]}
    )
    assert response.status_code == 200


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_read_update(api_client, recipe_data):
    response = api_client.get(f"/api/recipe/{recipe_data.expected_slug}/")
    assert response.status_code == 200

    recipe = json.loads(response.content)

    test_notes = [
        {"title": "My Test Title1", "text": "My Test Text1"},
        {"title": "My Test Title2", "text": "My Test Text2"},
    ]
    recipe["notes"] = test_notes

    test_categories = ["one", "two", "three"]
    recipe["categories"] = test_categories

    response = api_client.post(
        f"/api/recipe/{recipe_data.expected_slug}/update/", json=recipe
    )

    assert response.status_code == 200
    assert json.loads(response.text) == recipe_data.expected_slug

    response = api_client.get(f"/api/recipe/{recipe_data.expected_slug}/")

    recipe = json.loads(response.content)

    assert recipe["notes"] == test_notes
    assert recipe["categories"] == test_categories


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_rename(api_client, recipe_data):
    response = api_client.get(f"/api/recipe/{recipe_data.expected_slug}/")
    assert response.status_code == 200

    recipe = json.loads(response.content)
    new_name = recipe.get("name") + "-rename"
    new_slug = slugify(new_name)
    recipe["name"] = new_name

    response = api_client.post(
        f"/api/recipe/{recipe_data.expected_slug}/update/", json=recipe
    )

    assert response.status_code == 200
    assert json.loads(response.text) == new_slug

    recipe_data.expected_slug = new_slug


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_delete(api_client, recipe_data):
    response = api_client.delete(f"/api/recipe/{recipe_data.expected_slug}/delete/")
    assert response.status_code == 200
