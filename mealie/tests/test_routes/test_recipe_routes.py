import json

import pytest


class RecipeTestData:
    def __init__(self, url, expected_slug) -> None:
        self.url: str = url
        self.expected_slug: str = expected_slug


test_data = [
    RecipeTestData(
        url="https://www.bonappetit.com/recipe/rustic-shrimp-toasts",
        expected_slug="rustic-shrimp-toasts",
    ),
    RecipeTestData(
        url="https://www.allrecipes.com/recipe/282905/honey-garlic-shrimp/",
        expected_slug="honey-garlic-shrimp",
    ),
]


@pytest.mark.parametrize("recipe_data", test_data)
def test_create(api_client, recipe_data: RecipeTestData):
    payload = json.dumps({"url": recipe_data.url})
    response = api_client.post("/api/recipe/create-url/", payload)
    assert response.status_code == 201
    assert json.loads(response.text) == recipe_data.expected_slug


@pytest.mark.parametrize("recipe_data", test_data)
def test_read_update(api_client, recipe_data):
    response = api_client.get(f"/api/recipe/{recipe_data.expected_slug}/")
    assert response.status_code == 200

    recipe = json.loads(response.content)

    recipe["notes"] = [
        {"title": "My Test Title1", "text": "My Test Text1"},
        {"title": "My Test Title2", "text": "My Test Text2"},
    ]

    recipe["categories"] = ["one", "two", "three"]

    payload = json.dumps(recipe)

    response = api_client.post(
        f"/api/recipe/{recipe_data.expected_slug}/update/", payload
    )

    assert response.status_code == 200
    assert json.loads(response.text) == recipe_data.expected_slug


@pytest.mark.parametrize("recipe_data", test_data)
def test_delete(api_client, recipe_data):
    response = api_client.delete(f"/api/recipe/{recipe_data.expected_slug}/delete/")
    assert response.status_code == 200
