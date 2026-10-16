from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_create_tool_with_family_category_brand_model(api_client: TestClient, unique_user: TestUser):
    data = {
        "name": random_string(10),
        "family": "small_appliance",
        "category": "Mixing & Beating",
        "brand": "KitchenAid",
        "model": "Artisan 5KSM125",
    }

    response = api_client.post(api_routes.organizers_tools, json=data, headers=unique_user.token)
    assert response.status_code == 201
    item = response.json()

    assert item["family"] == data["family"]
    assert item["category"] == data["category"]
    assert item["brand"] == data["brand"]
    assert item["model"] == data["model"]

    # the full listing (used by the sortable tools table) must carry the same fields
    response = api_client.get(api_routes.organizers_tools, headers=unique_user.token)
    assert response.status_code == 200
    listed = next(i for i in response.json()["items"] if i["id"] == item["id"])
    assert listed["family"] == data["family"]
    assert listed["category"] == data["category"]
    assert listed["brand"] == data["brand"]
    assert listed["model"] == data["model"]


def test_create_tool_without_family_defaults_to_none(api_client: TestClient, unique_user: TestUser):
    data = {"name": random_string(10)}

    response = api_client.post(api_routes.organizers_tools, json=data, headers=unique_user.token)
    assert response.status_code == 201
    item = response.json()

    assert item["family"] is None
    assert item["category"] is None
    assert item["brand"] is None
    assert item["model"] is None


def test_create_tool_rejects_unknown_family(api_client: TestClient, unique_user: TestUser):
    data = {"name": random_string(10), "family": "not-a-real-family"}

    response = api_client.post(api_routes.organizers_tools, json=data, headers=unique_user.token)
    assert response.status_code == 422


def test_update_tool_family_category_brand_model(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(api_routes.organizers_tools, json={"name": random_string(10)}, headers=unique_user.token)
    assert response.status_code == 201
    item_id = response.json()["id"]

    update = {
        "name": random_string(10),
        "family": "manual_tool",
        "category": "Cutting",
        "brand": "Wüsthof",
        "model": "Classic",
    }
    response = api_client.put(api_routes.organizers_tools_item_id(item_id), json=update, headers=unique_user.token)
    assert response.status_code == 200
    item = response.json()

    assert item["family"] == update["family"]
    assert item["category"] == update["category"]
    assert item["brand"] == update["brand"]
    assert item["model"] == update["model"]
