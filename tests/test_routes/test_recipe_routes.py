import json

import pytest
from slugify import slugify
from tests.test_routes.utils.routes_data import RecipeTestData, raw_recipe, raw_recipe_no_image, recipe_test_data
from tests.utils.routes import RECIPES_ALL, RECIPES_CREATE, RECIPES_CREATE_URL, RECIPES_PREFIX


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_create_by_url(api_client, recipe_data: RecipeTestData):
    response = api_client.post(RECIPES_CREATE_URL, json={"url": recipe_data.url})
    assert response.status_code == 201
    assert json.loads(response.text) == recipe_data.expected_slug


def test_create_by_json(api_client):
    api_client.delete(f"{RECIPES_PREFIX}/banana-bread")
    response = api_client.post(RECIPES_CREATE, json=raw_recipe)

    assert response.status_code == 201
    assert json.loads(response.text) == "banana-bread"


def test_create_no_image(api_client):
    response = api_client.post(RECIPES_CREATE, json=raw_recipe_no_image)

    assert response.status_code == 201
    assert json.loads(response.text) == "banana-bread-no-image"


# def test_upload_image(api_client, test_image):
#     data = {"image": test_image.open("rb").read(), "extension": "jpg"}

#     response = api_client.post(
#         "{RECIPES_PREFIX}banana-bread-no-image/update/image/", files=data
#     )

#     assert response.status_code == 200

#     response = api_client.get("{RECIPES_PREFIX}banana-bread-no-image/update/image/")


def test_read_all_post(api_client):
    response = api_client.post(RECIPES_ALL, json={"properties": ["slug", "description", "rating"]})
    assert response.status_code == 200


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_read_update(api_client, recipe_data):
    response = api_client.get(f"{RECIPES_PREFIX}/{recipe_data.expected_slug}")
    assert response.status_code == 200

    recipe = json.loads(response.content)

    test_notes = [
        {"title": "My Test Title1", "text": "My Test Text1"},
        {"title": "My Test Title2", "text": "My Test Text2"},
    ]
    recipe["notes"] = test_notes

    test_categories = ["one", "two", "three"]
    recipe["recipeCategory"] = test_categories

    response = api_client.put(f"{RECIPES_PREFIX}/{recipe_data.expected_slug}", json=recipe)

    assert response.status_code == 200
    assert json.loads(response.text) == recipe_data.expected_slug

    response = api_client.get(f"{RECIPES_PREFIX}/{recipe_data.expected_slug}")

    recipe = json.loads(response.content)

    assert recipe["notes"] == test_notes
    assert recipe["recipeCategory"].sort() == test_categories.sort()


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_rename(api_client, recipe_data):
    response = api_client.get(f"{RECIPES_PREFIX}/{recipe_data.expected_slug}")
    assert response.status_code == 200

    recipe = json.loads(response.content)
    new_name = recipe.get("name") + "-rename"
    new_slug = slugify(new_name)
    recipe["name"] = new_name

    response = api_client.put(f"{RECIPES_PREFIX}/{recipe_data.expected_slug}", json=recipe)

    assert response.status_code == 200
    assert json.loads(response.text) == new_slug

    recipe_data.expected_slug = new_slug


@pytest.mark.parametrize("recipe_data", recipe_test_data)
def test_delete(api_client, recipe_data):
    response = api_client.delete(f"{RECIPES_PREFIX}/{recipe_data.expected_slug}")
    assert response.status_code == 200
