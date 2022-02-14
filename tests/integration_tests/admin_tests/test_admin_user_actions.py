from fastapi.testclient import TestClient

from tests import utils
from tests.utils import routes
from tests.utils.app_routes import AppRoutes
from tests.utils.factories import random_email, random_string
from tests.utils.fixture_schemas import TestUser


def generate_create_data() -> dict:
    return {
        "username": random_string(),
        "fullName": random_string(),
        "email": random_email(),
        "admin": False,
        "group": "Home",
        "advanced": False,
        "favoriteRecipes": [],
        "canInvite": False,
        "canManage": False,
        "canOrganize": False,
        "password": random_string(),
    }


def test_init_superuser(api_client: TestClient, admin_user: TestUser):
    response = api_client.get(routes.RoutesAdminUsers.item(admin_user.user_id), headers=admin_user.token)
    assert response.status_code == 200

    admin_data = response.json()

    assert admin_data["id"] == admin_user.user_id
    assert admin_data["groupId"] == admin_user.group_id

    assert admin_data["fullName"] == "Change Me"
    assert admin_data["email"] == "changeme@email.com"


def test_create_user(api_client: TestClient, api_routes: AppRoutes, admin_token):
    create_data = generate_create_data()
    response = api_client.post(routes.RoutesAdminUsers.base, json=create_data, headers=admin_token)
    assert response.status_code == 201

    form_data = {"username": create_data["email"], "password": create_data["password"]}
    header = utils.login(form_data=form_data, api_client=api_client, api_routes=api_routes)

    response = api_client.get(routes.RoutesUsers.self, headers=header)
    assert response.status_code == 200

    user_data = response.json()

    assert user_data["fullName"] == create_data["fullName"]
    assert user_data["email"] == create_data["email"]
    assert user_data["group"] == create_data["group"]
    assert user_data["admin"] == create_data["admin"]


def test_create_user_as_non_admin(api_client: TestClient, user_token):
    create_data = generate_create_data()
    response = api_client.post(routes.RoutesAdminUsers.base, json=create_data, headers=user_token)
    assert response.status_code == 403


def test_update_user(api_client: TestClient, admin_user: TestUser):
    # Create a new user
    create_data = generate_create_data()
    response = api_client.post(routes.RoutesAdminUsers.base, json=create_data, headers=admin_user.token)
    assert response.status_code == 201
    update_data = response.json()

    # Change data
    update_data["fullName"] = random_string()
    update_data["email"] = random_email()

    response = api_client.put(
        routes.RoutesAdminUsers.item(update_data["id"]), headers=admin_user.token, json=update_data
    )

    assert response.status_code == 200


def test_update_other_user_as_not_admin(api_client: TestClient, unique_user: TestUser, g2_user: TestUser):
    update_data = {
        "id": unique_user.user_id,
        "fullName": "Updated Name",
        "email": "changeme@email.com",
        "group": "Home",
        "admin": True,
    }
    response = api_client.put(
        routes.RoutesAdminUsers.item(g2_user.user_id), headers=unique_user.token, json=update_data
    )

    assert response.status_code == 403


def test_self_demote_admin(api_client: TestClient, admin_user: TestUser):
    response = api_client.get(routes.RoutesUsers.self, headers=admin_user.token)
    assert response.status_code == 200

    user_data = response.json()
    user_data["admin"] = False

    response = api_client.put(
        routes.RoutesAdminUsers.item(admin_user.user_id), headers=admin_user.token, json=user_data
    )

    assert response.status_code == 403


def test_self_promote_admin(api_client: TestClient, unique_user: TestUser):
    update_data = {
        "id": unique_user.user_id,
        "fullName": "Updated Name",
        "email": "user@email.com",
        "group": "Home",
        "admin": True,
    }
    response = api_client.put(
        routes.RoutesAdminUsers.item(unique_user.user_id), headers=unique_user.token, json=update_data
    )

    assert response.status_code == 403


def test_delete_user(api_client: TestClient, admin_token, unique_user: TestUser):
    response = api_client.delete(routes.RoutesAdminUsers.item(unique_user.user_id), headers=admin_token)
    assert response.status_code == 200
