import json

from fastapi.testclient import TestClient

from tests.utils.app_routes import AppRoutes
from tests.utils.fixture_schemas import TestUser


def test_failed_login(api_client: TestClient, api_routes: AppRoutes):
    form_data = {"username": "changeme@email.com", "password": "WRONG_PASSWORD"}
    response = api_client.post(api_routes.auth_token, form_data)

    assert response.status_code == 401


def test_superuser_login(api_client: TestClient, api_routes: AppRoutes, admin_token):
    form_data = {"username": "changeme@email.com", "password": "MyPassword"}
    response = api_client.post(api_routes.auth_token, form_data)

    assert response.status_code == 200
    new_token = json.loads(response.text).get("access_token")

    response = api_client.get(api_routes.users_self, headers=admin_token)
    assert response.status_code == 200

    return {"Authorization": f"Bearer {new_token}"}


def test_user_token_refresh(api_client: TestClient, api_routes: AppRoutes, admin_user: TestUser):
    response = api_client.post(api_routes.auth_refresh, headers=admin_user.token)
    response = api_client.get(api_routes.users_self, headers=admin_user.token)
    assert response.status_code == 200
