import json

from fastapi.testclient import TestClient

from tests.app_routes import AppRoutes
from tests.utils.fixture_schemas import TestUser


def test_init_superuser(api_client: TestClient, api_routes: AppRoutes, admin_token, admin_user: TestUser):
    response = api_client.get(api_routes.users_id(1), headers=admin_token)
    assert response.status_code == 200

    admin_data = response.json()

    assert admin_data["id"] == admin_user.user_id
    assert admin_data["groupId"] == admin_user.group_id

    assert admin_data["fullName"] == "Change Me"
    assert admin_data["email"] == "changeme@email.com"


def test_create_user(api_client: TestClient, api_routes: AppRoutes, admin_token):
    create_data = {
        "fullName": "My New User",
        "email": "newuser@email.com",
        "password": "MyStrongPassword",
        "group": "Home",
        "admin": False,
        "tokens": [],
    }

    response = api_client.post(api_routes.users, json=create_data, headers=admin_token)

    assert response.status_code == 201

    user_data = response.json()

    assert user_data["fullName"] == create_data["fullName"]
    assert user_data["email"] == create_data["email"]
    assert user_data["group"] == create_data["group"]
    assert user_data["admin"] == create_data["admin"]


def test_create_user_as_non_admin(api_client: TestClient, api_routes: AppRoutes, user_token):
    create_data = {
        "fullName": "My New User",
        "email": "newuser@email.com",
        "password": "MyStrongPassword",
        "group": "Home",
        "admin": False,
        "tokens": [],
    }

    response = api_client.post(api_routes.users, json=create_data, headers=user_token)

    assert response.status_code == 403


def test_update_user(api_client: TestClient, api_routes: AppRoutes, admin_token):
    update_data = {"id": 1, "fullName": "Updated Name", "email": "changeme@email.com", "group": "Home", "admin": True}
    response = api_client.put(api_routes.users_id(1), headers=admin_token, json=update_data)

    assert response.status_code == 200
    assert json.loads(response.text).get("access_token")


def test_update_other_user_as_not_admin(api_client: TestClient, api_routes: AppRoutes, unique_user: TestUser):
    update_data = {"id": 1, "fullName": "Updated Name", "email": "changeme@email.com", "group": "Home", "admin": True}
    response = api_client.put(api_routes.users_id(1), headers=unique_user.token, json=update_data)

    assert response.status_code == 403


def test_self_demote_admin(api_client: TestClient, api_routes: AppRoutes, admin_token):
    update_data = {"fullName": "Updated Name", "email": "changeme@email.com", "group": "Home", "admin": False}
    response = api_client.put(api_routes.users_id(1), headers=admin_token, json=update_data)

    assert response.status_code == 403


def test_self_promote_admin(api_client: TestClient, api_routes: AppRoutes, user_token):
    update_data = {"id": 3, "fullName": "Updated Name", "email": "user@email.com", "group": "Home", "admin": True}
    response = api_client.put(api_routes.users_id(2), headers=user_token, json=update_data)

    assert response.status_code == 403


def test_delete_user(api_client: TestClient, api_routes: AppRoutes, admin_token):
    response = api_client.delete(api_routes.users_id(2), headers=admin_token)

    assert response.status_code == 200
