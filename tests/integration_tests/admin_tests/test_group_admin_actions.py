import json

from fastapi.testclient import TestClient

from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/admin/groups"

    def item(id: str) -> str:
        return f"{Routes.base}/{id}"


def test_create_group(api_client: TestClient, admin_token):
    response = api_client.post(Routes.base, json={"name": random_string()}, headers=admin_token)
    assert response.status_code == 201


def test_user_cant_create_group(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(Routes.base, json={"name": random_string()}, headers=unique_user.token)
    assert response.status_code == 403


def test_home_group_not_deletable(api_client: TestClient, admin_token):
    response = api_client.delete(Routes.item(1), headers=admin_token)

    assert response.status_code == 400


def test_delete_group(api_client: TestClient, admin_token):
    response = api_client.post(Routes.base, json={"name": random_string()}, headers=admin_token)
    assert response.status_code == 201

    group_id = json.loads(response.text)["id"]

    response = api_client.delete(Routes.item(group_id), headers=admin_token)

    assert response.status_code == 200

    # Ensure Group is Deleted
    response = api_client.get(Routes.base, headers=admin_token)

    for g in response.json():
        assert g["id"] != group_id
