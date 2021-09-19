import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_ingredient import CreateIngredientUnit
from tests.utils.factories import random_bool, random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/units"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"


@pytest.fixture(scope="function")
def unit(api_client: TestClient, unique_user: TestUser) -> dict:
    data = CreateIngredientUnit(
        name=random_string(10),
        description=random_string(10),
        fraction=random_bool(),
        abbreviation=random_string(3) + ".",
    ).dict(by_alias=True)

    response = api_client.post(Routes.base, json=data, headers=unique_user.token)

    assert response.status_code == 201

    yield response.json()

    response = api_client.delete(Routes.item(response.json()["id"]), headers=unique_user.token)


def test_create_unit(api_client: TestClient, unique_user: TestUser):
    data = CreateIngredientUnit(
        name=random_string(10),
        description=random_string(10),
    ).dict(by_alias=True)

    response = api_client.post(Routes.base, json=data, headers=unique_user.token)
    assert response.status_code == 201


def test_read_unit(api_client: TestClient, unit: dict, unique_user: TestUser):
    response = api_client.get(Routes.item(unit["id"]), headers=unique_user.token)
    assert response.status_code == 200

    as_json = response.json()

    assert as_json["id"] == unit["id"]
    assert as_json["name"] == unit["name"]
    assert as_json["description"] == unit["description"]
    assert as_json["fraction"] == unit["fraction"]
    assert as_json["abbreviation"] == unit["abbreviation"]


def test_update_unit(api_client: TestClient, unit: dict, unique_user: TestUser):
    update_data = {
        "id": unit["id"],
        "name": random_string(10),
        "description": random_string(10),
        "fraction": not unit["fraction"],
        "abbreviation": random_string(3) + ".",
    }
    response = api_client.put(Routes.item(unit["id"]), json=update_data, headers=unique_user.token)
    assert response.status_code == 200
    as_json = response.json()

    assert as_json["id"] == unit["id"]
    assert as_json["name"] == update_data["name"]
    assert as_json["description"] == update_data["description"]
    assert as_json["fraction"] == update_data["fraction"]
    assert as_json["abbreviation"] == update_data["abbreviation"]


def test_delete_unit(api_client: TestClient, unit: dict, unique_user: TestUser):
    id = unit["id"]

    response = api_client.delete(Routes.item(id), headers=unique_user.token)

    assert response.status_code == 200

    response = api_client.get(Routes.item(id), headers=unique_user.token)
    assert response.status_code == 404
