import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/foods"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"


@pytest.fixture(scope="function")
def food(api_client: TestClient, unique_user: TestUser) -> dict:
    data = CreateIngredientFood(
        name=random_string(10),
        description=random_string(10),
    ).dict(by_alias=True)

    response = api_client.post(Routes.base, json=data, headers=unique_user.token)

    assert response.status_code == 201

    yield response.json()

    response = api_client.delete(Routes.item(response.json()["id"]), headers=unique_user.token)


def test_create_food(api_client: TestClient, unique_user: TestUser):
    data = CreateIngredientFood(
        name=random_string(10),
        description=random_string(10),
    ).dict(by_alias=True)

    response = api_client.post(Routes.base, json=data, headers=unique_user.token)
    assert response.status_code == 201


def test_read_food(api_client: TestClient, food: dict, unique_user: TestUser):
    response = api_client.get(Routes.item(food["id"]), headers=unique_user.token)
    assert response.status_code == 200

    as_json = response.json()

    assert as_json["id"] == food["id"]
    assert as_json["name"] == food["name"]
    assert as_json["description"] == food["description"]


def test_update_food(api_client: TestClient, food: dict, unique_user: TestUser):
    update_data = {
        "id": food["id"],
        "name": random_string(10),
        "description": random_string(10),
    }
    response = api_client.put(Routes.item(food["id"]), json=update_data, headers=unique_user.token)
    assert response.status_code == 200
    as_json = response.json()

    assert as_json["id"] == food["id"]
    assert as_json["name"] == update_data["name"]
    assert as_json["description"] == update_data["description"]


def test_delete_food(api_client: TestClient, food: dict, unique_user: TestUser):
    id = food["id"]

    response = api_client.delete(Routes.item(id), headers=unique_user.token)

    assert response.status_code == 200

    response = api_client.get(Routes.item(id), headers=unique_user.token)
    print(response.json())
    assert response.status_code == 404
