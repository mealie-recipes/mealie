from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from mealie.schema.static import recipe_keys
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/categories"
    recipes = "/api/recipes"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"

    def recipe(recipe_id: int) -> str:
        return f"{Routes.recipes}/{recipe_id}"


@dataclass
class TestRecipeCategory:
    id: int
    name: str
    slug: str
    recipes: list


@pytest.fixture(scope="function")
def category(api_client: TestClient, unique_user: TestUser) -> TestRecipeCategory:
    data = {"name": random_string(10)}

    response = api_client.post(Routes.base, json=data, headers=unique_user.token)

    assert response.status_code == 201

    as_json = response.json()

    yield TestRecipeCategory(
        id=as_json["id"],
        name=data["name"],
        slug=as_json["slug"],
        recipes=[],
    )

    try:
        response = api_client.delete(Routes.item(response.json()["slug"]), headers=unique_user.token)
    except Exception:
        pass


def test_create_category(api_client: TestClient, unique_user: TestUser):
    data = {"name": random_string(10)}
    response = api_client.post(Routes.base, json=data, headers=unique_user.token)
    assert response.status_code == 201


def test_read_category(api_client: TestClient, category: TestRecipeCategory, unique_user: TestUser):
    response = api_client.get(Routes.item(category.slug), headers=unique_user.token)
    assert response.status_code == 200

    as_json = response.json()
    assert as_json["id"] == category.id
    assert as_json["name"] == category.name


def test_update_category(api_client: TestClient, category: TestRecipeCategory, unique_user: TestUser):
    update_data = {
        "id": category.id,
        "name": random_string(10),
        "slug": category.slug,
    }

    response = api_client.put(Routes.item(category.slug), json=update_data, headers=unique_user.token)
    assert response.status_code == 200

    as_json = response.json()
    assert as_json["id"] == category.id
    assert as_json["name"] == update_data["name"]


def test_delete_category(api_client: TestClient, category: TestRecipeCategory, unique_user: TestUser):
    response = api_client.delete(Routes.item(category.slug), headers=unique_user.token)
    assert response.status_code == 200


def test_recipe_category_association(api_client: TestClient, category: TestRecipeCategory, unique_user: TestUser):
    # Setup Recipe
    recipe_data = {"name": random_string(10)}
    response = api_client.post(Routes.recipes, json=recipe_data, headers=unique_user.token)
    slug = response.json()
    assert response.status_code == 201

    # Get Recipe Data
    response = api_client.get(Routes.recipe(slug), headers=unique_user.token)
    as_json = response.json()
    as_json[recipe_keys.recipe_category] = [{"id": category.id, "name": category.name, "slug": category.slug}]

    # Update Recipe
    response = api_client.put(Routes.recipe(slug), json=as_json, headers=unique_user.token)
    assert response.status_code == 200

    # Get Recipe Data
    response = api_client.get(Routes.recipe(slug), headers=unique_user.token)
    as_json = response.json()
    assert as_json[recipe_keys.recipe_category][0]["slug"] == category.slug
