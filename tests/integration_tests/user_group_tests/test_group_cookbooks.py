import pytest
from fastapi.testclient import TestClient


class Routes:
    base = "/api/groups/cookbooks"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"


@pytest.fixture()
def page_data():
    return {"name": "My New Page", "description": "", "position": 0, "categories": [], "groupId": 1}


def test_create_cookbook(api_client: TestClient, admin_token, page_data):
    response = api_client.post(Routes.base, json=page_data, headers=admin_token)

    assert response.status_code == 200


def test_read_cookbook(api_client: TestClient, page_data, admin_token):
    response = api_client.get(Routes.item(1), headers=admin_token)

    page_data["id"] = 1
    page_data["slug"] = "my-new-page"

    assert response.json() == page_data


def test_update_cookbook(api_client: TestClient, page_data, admin_token):
    page_data["id"] = 1
    page_data["name"] = "My New Name"
    response = api_client.put(Routes.item(1), json=page_data, headers=admin_token)

    assert response.status_code == 200


def test_delete_cookbook(api_client: TestClient, admin_token):
    response = api_client.delete(Routes.item(1), headers=admin_token)

    assert response.status_code == 200

    response = api_client.get(Routes.item(1), headers=admin_token)
    assert response.status_code == 404
