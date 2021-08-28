import json

import pytest
from fastapi.testclient import TestClient

from mealie.schema.user import SignUpToken
from tests.app_routes import AppRoutes


@pytest.fixture()
def active_link(api_client: TestClient, api_routes: AppRoutes, admin_token):
    data = {"name": "Fixture Token", "admin": True}

    response = api_client.post(api_routes.users_sign_ups, json=data, headers=admin_token)

    return SignUpToken(**json.loads(response.text))


@pytest.fixture()
def sign_up_user():
    return {
        "fullName": "Test User",
        "email": "test_user@email.com",
        "admin": True,
        "group": "string",
        "password": "MySecretPassword",
    }


def test_create_sign_up_link(api_client: TestClient, api_routes: AppRoutes, admin_token):
    data = {"name": "Test Token", "admin": False}

    response = api_client.post(api_routes.users_sign_ups, json=data, headers=admin_token)
    assert response.status_code == 200


def test_new_user_signup(api_client: TestClient, api_routes: AppRoutes, active_link: SignUpToken, sign_up_user):

    # Creation
    response = api_client.post(api_routes.users_sign_ups_token(active_link.token), json=sign_up_user)
    assert response.status_code == 200

    # Login
    form_data = {"username": "test_user@email.com", "password": "MySecretPassword"}
    response = api_client.post(api_routes.auth_token, form_data)

    assert response.status_code == 200


def test_delete_sign_up_link(
    api_client: TestClient, api_routes: AppRoutes, admin_token, active_link: SignUpToken, sign_up_user
):
    response = api_client.delete(api_routes.users_sign_ups_token(active_link.token), headers=admin_token)
    assert response.status_code == 200

    # Validate admin_token is Gone
    response = api_client.get(api_routes.users_sign_ups, headers=admin_token)
    assert sign_up_user not in json.loads(response.content)
