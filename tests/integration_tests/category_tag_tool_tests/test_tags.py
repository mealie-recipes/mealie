from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/tags"
    recipes = "/api/recipes"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"

    def recipe(recipe_id: int) -> str:
        return f"{Routes.recipes}/{recipe_id}"


@dataclass
class TestRecipeTag:
    id: int
    name: str
    slug: str
    recipes: list


@pytest.fixture(scope="function")
def tag(api_client: TestClient, unique_user: TestUser) -> TestRecipeTag:
    data = {"name": random_string(10)}

    response = api_client.post(Routes.base, json=data, headers=unique_user.token)

    assert response.status_code == 201

    as_json = response.json()

    yield TestRecipeTag(
        id=as_json["id"],
        name=data["name"],
        slug=as_json["slug"],
        recipes=[],
    )

    try:
        response = api_client.delete(Routes.item(response.json()["slug"]), headers=unique_user.token)
    except Exception:
        pass


def test_create_tag(api_client: TestClient, unique_user: TestUser):
    data = {"name": random_string(10)}
    response = api_client.post(Routes.base, json=data, headers=unique_user.token)
    assert response.status_code == 201


def test_read_tag(api_client: TestClient, tag: TestRecipeTag, unique_user: TestUser):
    response = api_client.get(Routes.item(tag.slug), headers=unique_user.token)
    assert response.status_code == 200

    as_json = response.json()
    assert as_json["id"] == tag.id
    assert as_json["name"] == tag.name


def test_update_tag(api_client: TestClient, tag: TestRecipeTag, unique_user: TestUser):
    update_data = {
        "id": tag.id,
        "name": random_string(10),
        "slug": tag.slug,
    }

    response = api_client.put(Routes.item(tag.slug), json=update_data, headers=unique_user.token)
    assert response.status_code == 200

    as_json = response.json()
    assert as_json["id"] == tag.id
    assert as_json["name"] == update_data["name"]


def test_delete_tag(api_client: TestClient, tag: TestRecipeTag, unique_user: TestUser):
    response = api_client.delete(Routes.item(tag.slug), headers=unique_user.token)
    assert response.status_code == 200


def test_recipe_tag_association(api_client: TestClient, tag: TestRecipeTag, unique_user: TestUser):
    # Setup Recipe
    recipe_data = {"name": random_string(10)}
    response = api_client.post(Routes.recipes, json=recipe_data, headers=unique_user.token)
    slug = response.json()
    assert response.status_code == 201

    # Get Recipe Data
    response = api_client.get(Routes.recipe(slug), headers=unique_user.token)
    as_json = response.json()
    as_json["tags"] = [{"id": tag.id, "name": tag.name, "slug": tag.slug}]

    # Update Recipe
    response = api_client.put(Routes.recipe(slug), json=as_json, headers=unique_user.token)
    assert response.status_code == 200

    # Get Recipe Data
    response = api_client.get(Routes.recipe(slug), headers=unique_user.token)
    as_json = response.json()
    assert as_json["tags"][0]["slug"] == tag.slug
