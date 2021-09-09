import json

from fastapi.testclient import TestClient
from pytest import fixture

from tests.app_routes import AppRoutes


@fixture
def long_live_token(api_client: TestClient, api_routes: AppRoutes, admin_token):
    response = api_client.post(api_routes.users_api_tokens, json={"name": "Test Fixture Token"}, headers=admin_token)
    assert response.status_code == 201

    return {"Authorization": f"Bearer {json.loads(response.text).get('token')}"}


def test_api_token_creation(api_client: TestClient, api_routes: AppRoutes, admin_token):
    response = api_client.post(api_routes.users_api_tokens, json={"name": "Test API Token"}, headers=admin_token)
    assert response.status_code == 201


def test_use_token(api_client: TestClient, api_routes: AppRoutes, long_live_token):
    response = api_client.get(api_routes.users, headers=long_live_token)

    assert response.status_code == 200


def test_delete_token(api_client: TestClient, api_routes: AppRoutes, admin_token):
    response = api_client.delete(api_routes.users_api_tokens_token_id(1), headers=admin_token)
    assert response.status_code == 200

    response = api_client.delete(api_routes.users_api_tokens_token_id(2), headers=admin_token)
    assert response.status_code == 200
