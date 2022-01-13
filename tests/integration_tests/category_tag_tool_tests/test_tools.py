from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/tools"
    recipes = "/api/recipes"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"

    def recipe(recipe_id: int) -> str:
        return f"{Routes.recipes}/{recipe_id}"


@dataclass
class TestRecipeTool:
    id: int
    name: str
    slug: str
    on_hand: bool
    recipes: list


@pytest.fixture(scope="function")
def tool(api_client: TestClient, unique_user: TestUser) -> TestRecipeTool:
    data = {"name": random_string(10)}

    response = api_client.post(Routes.base, json=data, headers=unique_user.token)

    assert response.status_code == 201

    as_json = response.json()

    yield TestRecipeTool(
        id=as_json["id"],
        name=data["name"],
        slug=as_json["slug"],
        on_hand=as_json["onHand"],
        recipes=[],
    )

    try:
        response = api_client.delete(Routes.item(response.json()["id"]), headers=unique_user.token)
    except Exception:
        pass


def test_create_tool(api_client: TestClient, unique_user: TestUser):
    data = {"name": random_string(10)}

    response = api_client.post(Routes.base, json=data, headers=unique_user.token)
    assert response.status_code == 201


def test_read_tool(api_client: TestClient, tool: TestRecipeTool, unique_user: TestUser):
    response = api_client.get(Routes.item(tool.id), headers=unique_user.token)
    assert response.status_code == 200

    as_json = response.json()
    assert as_json["id"] == tool.id
    assert as_json["name"] == tool.name


def test_update_tool(api_client: TestClient, tool: TestRecipeTool, unique_user: TestUser):
    update_data = {
        "id": tool.id,
        "name": random_string(10),
        "slug": tool.slug,
        "on_hand": True,
    }

    response = api_client.put(Routes.item(tool.id), json=update_data, headers=unique_user.token)
    assert response.status_code == 200

    as_json = response.json()
    assert as_json["id"] == tool.id
    assert as_json["name"] == update_data["name"]


def test_delete_tool(api_client: TestClient, tool: TestRecipeTool, unique_user: TestUser):
    response = api_client.delete(Routes.item(tool.id), headers=unique_user.token)
    assert response.status_code == 200


def test_recipe_tool_association(api_client: TestClient, tool: TestRecipeTool, unique_user: TestUser):
    # Setup Recipe
    recipe_data = {"name": random_string(10)}
    response = api_client.post(Routes.recipes, json=recipe_data, headers=unique_user.token)
    slug = response.json()
    assert response.status_code == 201

    # Get Recipe Data
    response = api_client.get(Routes.recipe(slug), headers=unique_user.token)
    as_json = response.json()
    as_json["tools"] = [{"id": tool.id, "name": tool.name, "slug": tool.slug}]

    # Update Recipe
    response = api_client.put(Routes.recipe(slug), json=as_json, headers=unique_user.token)
    assert response.status_code == 200

    # Get Recipe Data
    response = api_client.get(Routes.recipe(slug), headers=unique_user.token)
    as_json = response.json()
    assert as_json["tools"][0]["id"] == tool.id
