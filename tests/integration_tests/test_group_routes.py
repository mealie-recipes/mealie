import json

import pytest
from fastapi.testclient import TestClient
from tests.app_routes import AppRoutes


@pytest.fixture
def group_data():
    return {"name": "Test Group"}


def test_create_group(api_client: TestClient, api_routes: AppRoutes, token):
    response = api_client.post(api_routes.groups, json={"name": "Test Group"}, headers=token)

    assert response.status_code == 201


def test_get_self_group(api_client: TestClient, api_routes: AppRoutes, token):
    response = api_client.get(api_routes.groups, headers=token)

    assert response.status_code == 200
    assert len(json.loads(response.text)) >= 2


def test_update_group(api_client: TestClient, api_routes: AppRoutes, token):
    new_data = {
        "name": "New Group Name",
        "id": 2,
        "categories": [],
        "webhookUrls": [],
        "webhookTime": "00:00",
        "webhookEnable": False,
        "users": [],
        "mealplans": [],
    }
    # Test Update
    response = api_client.put(api_routes.groups_id(2), json=new_data, headers=token)
    assert response.status_code == 200
    
    # Validate Changes
    response = api_client.get(api_routes.groups, headers=token)
    all_groups = json.loads(response.text)
    id_2 = filter(lambda x: x["id"] == 2, all_groups)
    assert next(id_2) == new_data


def test_home_group_not_deletable(api_client: TestClient, api_routes: AppRoutes, token):
    response = api_client.delete(api_routes.groups_id(1), headers=token)

    assert response.status_code == 400


def test_delete_group(api_client: TestClient, api_routes: AppRoutes, token):
    response = api_client.delete(api_routes.groups_id(2), headers=token)

    assert response.status_code == 200
