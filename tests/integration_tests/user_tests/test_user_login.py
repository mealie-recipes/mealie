import json

from fastapi.testclient import TestClient

from tests.app_routes import AppRoutes


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
