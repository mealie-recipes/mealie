import json

from fastapi.testclient import TestClient

from .app_routes import AppRoutes


def login(form_data, api_client: TestClient, api_routes: AppRoutes):
    response = api_client.post(api_routes.auth_token, form_data)
    assert response.status_code == 200
    token = json.loads(response.text).get("access_token")
    return {"Authorization": f"Bearer {token}"}
