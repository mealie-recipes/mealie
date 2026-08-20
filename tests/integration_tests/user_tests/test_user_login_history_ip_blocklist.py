from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_email
from tests.utils.fixture_schemas import TestUser

USERS_LOGIN_HISTORY = "/api/users/getLoginHistory"
USERS_IP_BLOCKLIST_ADD = "/api/users/self/ip-blocklist"


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


def test_blocked_ip_returns_403_with_detail(api_client: TestClient, unique_user_fn_scoped: TestUser):
    history_response = api_client.get(USERS_LOGIN_HISTORY, headers=unique_user_fn_scoped.token)
    assert history_response.status_code == 200

    items = history_response.json().get("items", [])
    assert items
    ip = items[0].get("ipAddress")
    assert ip

    block_response = api_client.post(
        USERS_IP_BLOCKLIST_ADD,
        json={"user_id": str(unique_user_fn_scoped.user_id), "ip_address": ip, "reason": "test block"},
        headers=unique_user_fn_scoped.token,
    )
    assert block_response.status_code == 200

    response = _login_with_credentials(api_client, unique_user_fn_scoped.email, unique_user_fn_scoped.password)
    assert response.status_code == 403
    assert "Your IP address is blocked" in response.json().get("detail", "")


def test_get_login_history_contains_is_blocked_flag(api_client: TestClient, unique_user_fn_scoped: TestUser):
    history_response = api_client.get(USERS_LOGIN_HISTORY, headers=unique_user_fn_scoped.token)
    assert history_response.status_code == 200

    items = history_response.json().get("items", [])
    assert items
    ip = items[0].get("ipAddress")
    assert ip

    block_response = api_client.post(
        USERS_IP_BLOCKLIST_ADD,
        json={"user_id": str(unique_user_fn_scoped.user_id), "ip_address": ip, "reason": "mark isBlocked"},
        headers=unique_user_fn_scoped.token,
    )
    assert block_response.status_code in [200, 400]

    response = api_client.get(USERS_LOGIN_HISTORY, headers=unique_user_fn_scoped.token)
    assert response.status_code == 200

    items = response.json().get("items", [])
    assert any(item.get("ipAddress") == ip and item.get("isBlocked") is True for item in items)


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
