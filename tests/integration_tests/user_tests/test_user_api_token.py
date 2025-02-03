import json

from fastapi.testclient import TestClient
from pytest import fixture

from tests.utils import api_routes


@fixture
def long_live_token(api_client: TestClient, admin_token):
    response = api_client.post(api_routes.users_api_tokens, json={"name": "Test Fixture Token"}, headers=admin_token)
    assert response.status_code == 201

    return {"Authorization": f"Bearer {json.loads(response.text).get('token')}"}


def test_api_token_creation(api_client: TestClient, admin_token):
    response = api_client.post(api_routes.users_api_tokens, json={"name": "Test API Token"}, headers=admin_token)
    assert response.status_code == 201
    assert response.json()["token"]


def test_api_token_private(api_client: TestClient, admin_token):
    response = api_client.post(api_routes.users_api_tokens, json={"name": "Test API Token"}, headers=admin_token)
    assert response.status_code == 201

    response = api_client.get(api_routes.users, headers=admin_token, params={"perPage": -1})
    assert response.status_code == 200
    for user in response.json()["items"]:
        for user_token in user["tokens"] or []:
            assert "token" not in user_token

    response = api_client.get(api_routes.users_self, headers=admin_token)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["tokens"]
    for user_token in response_json["tokens"]:
        assert "token" not in user_token


def test_use_token(api_client: TestClient, long_live_token):
    response = api_client.get(api_routes.users, headers=long_live_token)

    assert response.status_code == 200


def test_delete_token(api_client: TestClient, admin_token):
    response = api_client.delete(api_routes.users_api_tokens_token_id(1), headers=admin_token)
    assert response.status_code == 200

    response = api_client.delete(api_routes.users_api_tokens_token_id(2), headers=admin_token)
    assert response.status_code == 200
