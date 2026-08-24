import os

import jwt
import pytest
from fastapi.testclient import TestClient

from mealie.core.config import get_app_settings
from mealie.core.security import ALGORITHM
from mealie.services.user_services.user_service import UserService
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def decode_token(token: str) -> dict:
    return jwt.decode(token, get_app_settings().SECRET, algorithms=[ALGORITHM])


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def log_in_for_token(api_client: TestClient, user: TestUser, remember_me: bool = False) -> str:
    """Logs in and returns the raw token.

    `utils.login` returns ready-made headers and drops the token itself, which these tests need in
    order to read the claims back out of it.
    """
    form_data = {
        "username": user.email,
        "password": user.password,
        "remember_me": str(remember_me).lower(),
    }
    response = api_client.post(api_routes.auth_token, data=form_data)
    assert response.status_code == 200

    return response.json()["access_token"]


def test_failed_login(api_client: TestClient):
    settings = get_app_settings()

    form_data = {"username": settings._DEFAULT_EMAIL, "password": "WRONG_PASSWORD"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 401


def test_superuser_login(api_client: TestClient, admin_token):
    settings = get_app_settings()

    form_data = {"username": settings._DEFAULT_EMAIL, "password": settings._DEFAULT_PASSWORD}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 200

    response = api_client.get(api_routes.users_self, headers=admin_token)
    assert response.status_code == 200


def test_login_response_reports_the_token_lifetime(api_client: TestClient, unique_user: TestUser):
    """Clients schedule their refresh off `expires_in`; without it they have to decode the token."""
    form_data = {"username": unique_user.email, "password": unique_user.password}
    response = api_client.post(api_routes.auth_token, data=form_data)
    assert response.status_code == 200

    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == get_app_settings().TOKEN_TIME * 60 * 60

    payload = decode_token(body["access_token"])
    assert payload["exp"] - payload["iat"] == body["expires_in"]


def test_remember_me_does_not_change_the_session_length(api_client: TestClient, unique_user: TestUser):
    """Remember-me decides whether the client persists the token, not how long it stays valid.

    It used to widen the token's lifetime instead, which made the checkbox a no-op whenever
    TOKEN_TIME was already longer than the remember-me window.
    """
    remembered = decode_token(log_in_for_token(api_client, unique_user, remember_me=True))
    plain = decode_token(log_in_for_token(api_client, unique_user, remember_me=False))

    expected = get_app_settings().TOKEN_TIME * 60 * 60
    assert remembered["exp"] - remembered["iat"] == expected
    assert plain["exp"] - plain["iat"] == expected

    # ...and the choice still travels on the token, for the client to act on
    assert remembered["rme"] is True
    assert plain["rme"] is False


@pytest.mark.parametrize("remember_me", [True, False], ids=["remembered", "not remembered"])
def test_login_sets_the_session_cookie(api_client: TestClient, unique_user: TestUser, remember_me: bool):
    """The server owns the cookie now.

    Safari caps anything written through `document.cookie` at seven days regardless of max-age, so a
    client-written cookie silently truncated every iOS session. Persistence still follows remember-me:
    a max-age when it's ticked, a session cookie when it isn't.
    """
    form_data = {
        "username": unique_user.email,
        "password": unique_user.password,
        "remember_me": str(remember_me).lower(),
    }
    response = api_client.post(api_routes.auth_token, data=form_data)
    assert response.status_code == 200

    cookie = response.headers["set-cookie"]
    assert cookie.startswith("mealie.access_token=")
    assert "Path=/" in cookie
    assert ("Max-Age" in cookie) is remember_me


def test_refresh_renews_the_session_cookie(api_client: TestClient, unique_user: TestUser):
    """Refreshing has to re-send the cookie, or the browser keeps serving the superseded token."""
    token = log_in_for_token(api_client, unique_user, remember_me=True)

    response = api_client.post(api_routes.auth_refresh, headers=auth_header(token))
    assert response.status_code == 200

    cookie = response.headers["set-cookie"]
    assert f"mealie.access_token={response.json()['access_token']}" in cookie
    assert "Max-Age" in cookie


def test_logout_clears_the_session_cookie(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(api_routes.auth_logout, headers=unique_user.token)
    assert response.status_code == 200

    cookie = response.headers["set-cookie"]
    assert cookie.startswith("mealie.access_token=")
    assert "Max-Age=0" in cookie


def test_authenticates_from_the_session_cookie(api_client: TestClient, unique_user: TestUser):
    """The SPA sends a bearer header, but downloads opened outside it rely on the cookie."""
    token = log_in_for_token(api_client, unique_user)

    response = api_client.get(api_routes.users_self, headers={"Cookie": f"mealie.access_token={token}"})
    assert response.status_code == 200
    assert response.json()["id"] == str(unique_user.user_id)


def test_user_token_refresh(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(api_routes.auth_refresh, headers=unique_user.token)
    assert response.status_code == 200

    refreshed = response.json()
    assert refreshed["token_type"] == "bearer"
    # clients schedule their refresh off this, so it has to be the lifetime actually granted
    assert refreshed["expires_in"] == get_app_settings().TOKEN_TIME * 60 * 60

    # the point of refreshing is a token that works, so check it rather than just its shape
    response = api_client.get(api_routes.users_self, headers=auth_header(refreshed["access_token"]))
    assert response.status_code == 200
    assert response.json()["id"] == str(unique_user.user_id)


@pytest.mark.parametrize("remember_me", [True, False], ids=["remembered", "not remembered"])
def test_token_refresh_preserves_remember_me(api_client: TestClient, unique_user: TestUser, remember_me: bool):
    """A refreshed session must keep the remember-me choice, or it silently becomes a shorter one."""
    token = log_in_for_token(api_client, unique_user, remember_me=remember_me)
    assert decode_token(token)["rme"] is remember_me

    response = api_client.post(api_routes.auth_refresh, headers=auth_header(token))
    assert response.status_code == 200
    assert decode_token(response.json()["access_token"])["rme"] is remember_me


def test_api_tokens_cannot_be_refreshed(api_client: TestClient, admin_token):
    """An API token is revocable; exchanging one for a session token would outlive its revocation."""
    response = api_client.post(api_routes.users_api_tokens, json={"name": "Refresh Test Token"}, headers=admin_token)
    assert response.status_code == 201

    response = api_client.post(api_routes.auth_refresh, headers=auth_header(response.json()["token"]))
    assert response.status_code == 400


@pytest.mark.parametrize("use_token", [True, False], ids=["invalid token", "no token"])
def test_token_refresh_rejects_unauthenticated(api_client: TestClient, use_token: bool):
    headers = auth_header(random_string()) if use_token else {}
    response = api_client.post(api_routes.auth_refresh, headers=headers)
    assert response.status_code == 401


@pytest.mark.parametrize("use_token", [True, False], ids=["with token", "without token"])
def test_get_logged_in_user_invalid_token(api_client: TestClient, use_token: bool):
    headers = {"Authorization": f"Bearer {random_string()}"} if use_token else {}
    response = api_client.get(api_routes.users_self, headers=headers)
    assert response.status_code == 401


def test_user_lockout_after_bad_attemps(api_client: TestClient, unique_user: TestUser):
    """
    if the user has more than 5 bad login attempts the user will be locked out for 4 hours
    This only applies if there is a user in the database with the same username
    """
    database = unique_user.repos
    settings = get_app_settings()

    for _ in range(settings.SECURITY_MAX_LOGIN_ATTEMPTS):
        form_data = {"username": unique_user.email, "password": "bad_password"}
        response = api_client.post(api_routes.auth_token, data=form_data)

        assert response.status_code == 401

    valid_data = {"username": unique_user.email, "password": unique_user.password}
    response = api_client.post(api_routes.auth_token, data=valid_data)
    assert response.status_code == 423

    # Cleanup
    user_service = UserService(database)
    user = database.users.get_one(unique_user.user_id)
    user_service.unlock_user(user)


@pytest.mark.skipif(not os.environ.get("GITHUB_ACTIONS", False), reason="requires ldap service in github actions")
def test_ldap_user_login(api_client: TestClient):
    form_data = {"username": "bender", "password": "bender"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 200

    data = response.json()
    assert data is not None
    assert data.get("access_token") is not None

    response = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {data.get('access_token')}"})
    assert response.status_code == 200

    data = response.json()
    assert data.get("username") == "bender"
    assert data.get("fullName") == "Bender Bending Rodríguez"
    assert data.get("email") == "bender@planetexpress.com"
    assert data.get("admin") is False


@pytest.mark.skipif(not os.environ.get("GITHUB_ACTIONS", False), reason="requires ldap service in github actions")
def test_ldap_user_login_bad_password(api_client: TestClient):
    form_data = {"username": "bender", "password": "BAD_PASS"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 401


@pytest.mark.skipif(not os.environ.get("GITHUB_ACTIONS", False), reason="requires ldap service in github actions")
def test_ldap_admin_login(api_client: TestClient):
    form_data = {"username": "professor", "password": "professor"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 200

    data = response.json()
    assert data is not None
    assert data.get("access_token") is not None

    response = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {data.get('access_token')}"})
    assert response.status_code == 200

    data = response.json()
    assert data.get("username") == "professor"
    assert data.get("fullName") == "Hubert J. Farnsworth"
    assert data.get("email") in ["professor@planetexpress.com", "hubert@planetexpress.com"]
    assert data.get("admin") is True


@pytest.mark.skipif(not os.environ.get("GITHUB_ACTIONS", False), reason="requires ldap service in github actions")
def test_ldap_user_not_in_filter(api_client: TestClient):
    form_data = {"username": "amy", "password": "amy"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 401


@pytest.mark.skipif(not os.environ.get("GITHUB_ACTIONS", False), reason="requires ldap service in github actions")
def test_ldap_user_login_starttls(api_client: TestClient):
    settings = get_app_settings()
    settings.LDAP_ENABLE_STARTTLS = True

    form_data = {"username": "bender", "password": "bender"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 200

    data = response.json()
    assert data is not None
    assert data.get("access_token") is not None

    response = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {data.get('access_token')}"})
    assert response.status_code == 200

    data = response.json()
    assert data.get("username") == "bender"
    assert data.get("fullName") == "Bender Bending Rodríguez"
    assert data.get("email") == "bender@planetexpress.com"
    assert data.get("admin") is False

    get_app_settings.cache_clear()


@pytest.mark.skipif(not os.environ.get("GITHUB_ACTIONS", False), reason="requires ldap service in github actions")
def test_ldap_user_login_anonymous_bind(api_client: TestClient):
    settings = get_app_settings()
    settings.LDAP_QUERY_BIND = None
    settings.LDAP_QUERY_PASSWORD = None

    form_data = {"username": "bender", "password": "bender"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 200

    data = response.json()
    assert data is not None
    assert data.get("access_token") is not None

    response = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {data.get('access_token')}"})
    assert response.status_code == 200

    data = response.json()
    assert data.get("username") == "bender"
    assert data.get("fullName") == "Bender Bending Rodríguez"
    assert data.get("email") == "bender@planetexpress.com"
    assert data.get("admin") is False

    get_app_settings.cache_clear()


@pytest.mark.skipif(not os.environ.get("GITHUB_ACTIONS", False), reason="requires ldap service in github actions")
def test_ldap_user_login_no_filter(api_client: TestClient):
    settings = get_app_settings()
    settings.LDAP_USER_FILTER = None

    form_data = {"username": "amy", "password": "amy"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 200

    data = response.json()
    assert data is not None
    assert data.get("access_token") is not None

    response = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {data.get('access_token')}"})
    assert response.status_code == 200

    data = response.json()
    assert data.get("username") == "amy"
    assert data.get("fullName") == "Amy Wong"
    assert data.get("email") == "amy@planetexpress.com"
    assert data.get("admin") is False

    get_app_settings.cache_clear()


@pytest.mark.skipif(not os.environ.get("GITHUB_ACTIONS", False), reason="requires ldap service in github actions")
def test_ldap_user_login_simple_filter(api_client: TestClient):
    settings = get_app_settings()
    settings.LDAP_USER_FILTER = "(memberOf=cn=ship_crew,ou=people,dc=planetexpress,dc=com)"

    form_data = {"username": "bender", "password": "bender"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 200

    data = response.json()
    assert data is not None
    assert data.get("access_token") is not None

    response = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {data.get('access_token')}"})
    assert response.status_code == 200

    data = response.json()
    assert data.get("username") == "bender"
    assert data.get("fullName") == "Bender Bending Rodríguez"
    assert data.get("email") == "bender@planetexpress.com"
    assert data.get("admin") is False

    get_app_settings.cache_clear()


@pytest.mark.skipif(not os.environ.get("GITHUB_ACTIONS", False), reason="requires ldap service in github actions")
def test_ldap_user_login_complex_filter(api_client: TestClient):
    settings = get_app_settings()
    settings.LDAP_USER_FILTER = (
        "(&(objectClass=inetOrgPerson)(|(memberOf=cn=ship_crew,ou=people,dc=planetexpress,dc=com)"
        "(memberOf=cn=admin_staff,ou=people,dc=planetexpress,dc=com)))"
    )

    form_data = {"username": "professor", "password": "professor"}
    response = api_client.post(api_routes.auth_token, data=form_data)

    assert response.status_code == 200

    data = response.json()
    assert data is not None
    assert data.get("access_token") is not None

    response = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {data.get('access_token')}"})
    assert response.status_code == 200

    data = response.json()
    assert data.get("username") == "professor"
    assert data.get("fullName") == "Hubert J. Farnsworth"
    assert data.get("email") in ["professor@planetexpress.com", "hubert@planetexpress.com"]
    assert data.get("admin") is True

    get_app_settings.cache_clear()
