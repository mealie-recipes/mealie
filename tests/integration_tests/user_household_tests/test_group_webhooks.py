from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes, assert_deserialize, jsonify
from tests.utils.fixture_schemas import TestUser


@pytest.fixture()
def webhook_data():
    return {
        "enabled": True,
        "name": "Test-Name",
        "url": "https://my-fake-url.com",
        "time": "00:00",
        "scheduledTime": datetime.now(UTC),
    }


def test_create_webhook(api_client: TestClient, unique_user: TestUser, webhook_data):
    response = api_client.post(
        api_routes.households_webhooks,
        json=jsonify(webhook_data),
        headers=unique_user.token,
    )
    assert response.status_code == 201


def test_read_webhook(api_client: TestClient, unique_user: TestUser, webhook_data):
    response = api_client.post(
        api_routes.households_webhooks,
        json=jsonify(webhook_data),
        headers=unique_user.token,
    )
    item_id = response.json()["id"]

    response = api_client.get(api_routes.households_webhooks_item_id(item_id), headers=unique_user.token)
    webhook = assert_deserialize(response, 200)

    assert webhook["id"] == item_id
    assert webhook["name"] == webhook_data["name"]
    assert webhook["url"] == webhook_data["url"]
    assert webhook["scheduledTime"] == str(webhook_data["scheduledTime"].astimezone(UTC).time())
    assert webhook["enabled"] == webhook_data["enabled"]


def test_update_webhook(api_client: TestClient, webhook_data, unique_user: TestUser):
    response = api_client.post(
        api_routes.households_webhooks,
        json=jsonify(webhook_data),
        headers=unique_user.token,
    )
    item_dict = assert_deserialize(response, 201)
    item_id = item_dict["id"]

    webhook_data["name"] = "My New Name"
    webhook_data["url"] = "https://my-new-fake-url.com"
    webhook_data["enabled"] = False

    response = api_client.put(
        api_routes.households_webhooks_item_id(item_id),
        json=jsonify(webhook_data),
        headers=unique_user.token,
    )
    updated_webhook = assert_deserialize(response, 200)

    assert updated_webhook["name"] == webhook_data["name"]
    assert updated_webhook["url"] == webhook_data["url"]
    assert updated_webhook["enabled"] == webhook_data["enabled"]


def test_delete_webhook(api_client: TestClient, webhook_data, unique_user: TestUser):
    response = api_client.post(
        api_routes.households_webhooks,
        json=jsonify(webhook_data),
        headers=unique_user.token,
    )
    item_dict = assert_deserialize(response, 201)
    item_id = item_dict["id"]

    response = api_client.delete(api_routes.households_webhooks_item_id(item_id), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(api_routes.households_webhooks_item_id(item_id), headers=unique_user.token)
    assert response.status_code == 404
