import json

import pytest
from fastapi.testclient import TestClient

from tests.app_routes import AppRoutes


@pytest.fixture()
def page_data():
    return {"name": "My New Page", "description": "", "position": 0, "categories": [], "groupId": 1}


def test_create_cookbook(api_client: TestClient, api_routes: AppRoutes, admin_token, page_data):
    response = api_client.post(api_routes.group_cookbook, json=page_data, headers=admin_token)

    assert response.status_code == 200


def test_read_cookbook(api_client: TestClient, api_routes: AppRoutes, page_data, admin_token):
    response = api_client.get(api_routes.group_cookbook_id(1), headers=admin_token)

    page_data["id"] = 1
    page_data["slug"] = "my-new-page"

    assert json.loads(response.text) == page_data


def test_update_cookbook(api_client: TestClient, api_routes: AppRoutes, page_data, admin_token):
    page_data["id"] = 1
    page_data["name"] = "My New Name"
    response = api_client.put(api_routes.group_cookbook_id(1), json=page_data, headers=admin_token)

    assert response.status_code == 200


def test_delete_cookbook(api_client: TestClient, api_routes: AppRoutes, admin_token):
    response = api_client.delete(api_routes.group_cookbook_id(1), headers=admin_token)

    assert response.status_code == 200

    response = api_client.get(api_routes.group_cookbook_id(1), headers=admin_token)
    assert response.status_code == 404
