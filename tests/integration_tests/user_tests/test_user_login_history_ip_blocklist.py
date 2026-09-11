import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_email
from tests.utils.fixture_schemas import TestUser

USERS_LOGIN_HISTORY = "/api/users/getLoginHistory"
USERS_IP_BLOCKLIST_ADD = "/api/users/self/ip-blocklist"
AUTH_LOGIN = "/api/auth/login"
TEST_CLIENT_IP = "203.0.113.50"


@pytest.fixture
def client_ip(monkeypatch):
    from mealie.routes.auth import auth as auth_routes

    monkeypatch.setattr(auth_routes, "_get_client_ip", lambda request: TEST_CLIENT_IP)
    return TEST_CLIENT_IP


def _login_with_credentials(api_client: TestClient, username: str, password: str):
    return api_client.post(api_routes.auth_token, data={"username": username, "password": password})


def test_failed_login_writes_username_history(api_client: TestClient, unfiltered_database):
    username = random_email()

    before_rows = unfiltered_database.login_history.multi_query({"username": username}, limit=200)
    response = _login_with_credentials(api_client, username, "bad_password")
    after_rows = unfiltered_database.login_history.multi_query({"username": username}, limit=200)

    assert response.status_code == 401
    assert len(after_rows) == len(before_rows) + 1
    assert any((not row.success) and row.username == username for row in after_rows)


def test_success_login_writes_username_history(
    api_client: TestClient, unique_user_fn_scoped: TestUser, unfiltered_database
):
    username = unique_user_fn_scoped.email

    before_rows = unfiltered_database.login_history.multi_query(
        {"username": username, "success": True},
        limit=500,
    )
    response = _login_with_credentials(api_client, username, unique_user_fn_scoped.password)
    after_rows = unfiltered_database.login_history.multi_query(
        {"username": username, "success": True},
        limit=500,
    )

    assert response.status_code == 200
    assert len(after_rows) == len(before_rows) + 1


def test_blocked_ip_returns_403_with_detail(api_client: TestClient, unique_user_fn_scoped: TestUser, client_ip: str):
    _login_with_credentials(api_client, unique_user_fn_scoped.email, unique_user_fn_scoped.password)

    block_response = api_client.post(
        USERS_IP_BLOCKLIST_ADD,
        json={"user_id": str(unique_user_fn_scoped.user_id), "ip_address": client_ip, "reason": "test block"},
        headers=unique_user_fn_scoped.token,
    )
    assert block_response.status_code == 200

    response = _login_with_credentials(api_client, unique_user_fn_scoped.email, unique_user_fn_scoped.password)
    assert response.status_code == 403
    assert "Your IP address is blocked" in response.json().get("detail", "")


def test_get_login_history_contains_is_blocked_flag(
    api_client: TestClient, unique_user_fn_scoped: TestUser, client_ip: str
):
    _login_with_credentials(api_client, unique_user_fn_scoped.email, unique_user_fn_scoped.password)

    block_response = api_client.post(
        USERS_IP_BLOCKLIST_ADD,
        json={"user_id": str(unique_user_fn_scoped.user_id), "ip_address": client_ip, "reason": "mark isBlocked"},
        headers=unique_user_fn_scoped.token,
    )
    assert block_response.status_code in [200, 400]

    response = api_client.get(USERS_LOGIN_HISTORY, headers=unique_user_fn_scoped.token)
    assert response.status_code == 200

    items = response.json().get("items", [])
    assert any(item.get("ipAddress") == client_ip and item.get("isBlocked") is True for item in items)


def test_non_admin_cannot_query_other_user_login_history(api_client: TestClient, user_tuple: list[TestUser]):
    user1, user2 = user_tuple

    response = api_client.get(
        USERS_LOGIN_HISTORY,
        params={"userId": str(user2.user_id), "page": 1, "perPage": 10},
        headers=user1.token,
    )

    assert response.status_code == 403


def test_admin_cannot_block_cross_group_user(api_client: TestClient, admin_user: TestUser, g2_user: TestUser):
    response = api_client.post(
        USERS_IP_BLOCKLIST_ADD,
        json={"user_id": str(g2_user.user_id), "ip_address": "203.0.113.10", "reason": "cross-group test"},
        headers=admin_user.token,
    )

    assert response.status_code == 404


def test_failed_login_does_not_store_password_in_reason(
    api_client: TestClient, unique_user_fn_scoped: TestUser, unfiltered_database
):
    secret_password = "super_secret_password_123"
    username = unique_user_fn_scoped.email

    response = api_client.post(
        AUTH_LOGIN,
        data={"username": username, "password": secret_password},
    )
    assert response.status_code == 401

    rows = unfiltered_database.login_history.multi_query({"username": username}, limit=200)
    failed_rows = [row for row in rows if not row.success]
    assert failed_rows
    latest = failed_rows[-1]
    assert latest.reason == "invalid_credentials"
    assert secret_password not in (latest.reason or "")


def test_invalid_ip_rejected_on_blocklist_add(api_client: TestClient, unique_user_fn_scoped: TestUser):
    response = api_client.post(
        USERS_IP_BLOCKLIST_ADD,
        json={"ip_address": "not-an-ip", "reason": "invalid ip test"},
        headers=unique_user_fn_scoped.token,
    )
    assert response.status_code == 422


def test_refresh_token_blocked_when_ip_blocked(api_client: TestClient, unique_user_fn_scoped: TestUser, client_ip: str):
    _login_with_credentials(api_client, unique_user_fn_scoped.email, unique_user_fn_scoped.password)

    block_response = api_client.post(
        USERS_IP_BLOCKLIST_ADD,
        json={"user_id": str(unique_user_fn_scoped.user_id), "ip_address": client_ip, "reason": "refresh block test"},
        headers=unique_user_fn_scoped.token,
    )
    assert block_response.status_code == 200

    refresh_response = api_client.get(api_routes.auth_refresh, headers=unique_user_fn_scoped.token)
    assert refresh_response.status_code == 403
    assert "Your IP address is blocked" in refresh_response.json().get("detail", "")
