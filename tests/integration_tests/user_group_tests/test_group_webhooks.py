import pytest
from fastapi.testclient import TestClient

from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/webhooks"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"


@pytest.fixture()
def webhook_data():
    return {"enabled": True, "name": "Test-Name", "url": "https://my-fake-url.com", "time": "00:00"}


def test_create_webhook(api_client: TestClient, unique_user: TestUser, webhook_data):
    response = api_client.post(Routes.base, json=webhook_data, headers=unique_user.token)

    assert response.status_code == 201


def test_read_webhook(api_client: TestClient, unique_user: TestUser, webhook_data):
    response = api_client.post(Routes.base, json=webhook_data, headers=unique_user.token)
    response = api_client.get(Routes.item(1), headers=unique_user.token)

    webhook = response.json()

    print(webhook)

    assert webhook["id"]
    assert webhook["name"] == webhook_data["name"]
    assert webhook["url"] == webhook_data["url"]
    assert webhook["time"] == webhook_data["time"]
    assert webhook["enabled"] == webhook_data["enabled"]


def test_update_webhook(api_client: TestClient, webhook_data, unique_user: TestUser):
    webhook_data["id"] = 1
    webhook_data["name"] = "My New Name"
    webhook_data["url"] = "https://my-new-fake-url.com"
    webhook_data["time"] = "01:00"
    webhook_data["enabled"] = False

    response = api_client.put(Routes.item(1), json=webhook_data, headers=unique_user.token)

    assert response.status_code == 200

    updated_webhook = response.json()
    assert updated_webhook["name"] == webhook_data["name"]
    assert updated_webhook["url"] == webhook_data["url"]
    assert updated_webhook["time"] == webhook_data["time"]
    assert updated_webhook["enabled"] == webhook_data["enabled"]

    assert response.status_code == 200


def test_delete_webhook(api_client: TestClient, unique_user: TestUser):
    response = api_client.delete(Routes.item(1), headers=unique_user.token)

    assert response.status_code == 200

    response = api_client.get(Routes.item(1), headers=unique_user.token)
    assert response.status_code == 404
