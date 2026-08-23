from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from mealie.routes.auth import auth as auth_routes
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _enable_reverse_proxy_auth(monkeypatch: MonkeyPatch, header: str = "X-Forwarded-User") -> None:
    monkeypatch.setattr(type(auth_routes.settings), "REVERSE_PROXY_AUTH_READY", property(lambda self: True))
    monkeypatch.setattr(auth_routes.settings, "REVERSE_PROXY_AUTH_HEADER", header)


def test_reverse_proxy_login_disabled_returns_404(api_client: TestClient):
    response = api_client.get(api_routes.auth_reverse_proxy, headers={"X-Forwarded-User": "someone"})
    assert response.status_code == 404


def test_reverse_proxy_login_missing_header_returns_401(api_client: TestClient, monkeypatch: MonkeyPatch):
    _enable_reverse_proxy_auth(monkeypatch)
    response = api_client.get(api_routes.auth_reverse_proxy)
    assert response.status_code == 401


def test_reverse_proxy_login_existing_user(api_client: TestClient, monkeypatch: MonkeyPatch, unique_user: TestUser):
    _enable_reverse_proxy_auth(monkeypatch)
    response = api_client.get(api_routes.auth_reverse_proxy, headers={"X-Forwarded-User": unique_user.username})

    assert response.status_code == 200
    data = response.json()
    assert data.get("access_token") is not None

    response = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {data['access_token']}"})
    assert response.status_code == 200
    assert response.json()["username"] == unique_user.username


def test_reverse_proxy_login_creates_new_user(api_client: TestClient, monkeypatch: MonkeyPatch):
    _enable_reverse_proxy_auth(monkeypatch)
    monkeypatch.setattr(auth_routes.settings, "REVERSE_PROXY_AUTH_SIGNUP_ENABLED", True)

    username = random_string(10)
    response = api_client.get(api_routes.auth_reverse_proxy, headers={"X-Forwarded-User": username})

    assert response.status_code == 200
    assert response.json().get("access_token") is not None


def test_reverse_proxy_login_signup_disabled_returns_401(api_client: TestClient, monkeypatch: MonkeyPatch):
    _enable_reverse_proxy_auth(monkeypatch)
    monkeypatch.setattr(auth_routes.settings, "REVERSE_PROXY_AUTH_SIGNUP_ENABLED", False)

    username = random_string(10)
    response = api_client.get(api_routes.auth_reverse_proxy, headers={"X-Forwarded-User": username})

    assert response.status_code == 401
