import os

import pytest
from fastapi.testclient import TestClient

from mealie.core.dependencies import dependencies
from mealie.core.config import get_app_settings
from mealie.services.user_services.user_service import UserService
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _refresh_dependency_settings() -> None:
    get_app_settings.cache_clear()
    dependencies.settings = get_app_settings()


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


def test_user_token_refresh(api_client: TestClient, admin_user: TestUser):
    response = api_client.post(api_routes.auth_refresh, headers=admin_user.token)
    response = api_client.get(api_routes.users_self, headers=admin_user.token)
    assert response.status_code == 200


def test_proxy_header_auth_existing_user(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("PROXY_AUTH_ENABLED", "true")
    monkeypatch.setenv("PROXY_AUTH_HEADER", "Remote-User")
    monkeypatch.setenv("TRUSTED_PROXY", "testclient")
    _refresh_dependency_settings()

    response = api_client.get(api_routes.users_self, headers={"Remote-User": unique_user.username})
    assert response.status_code == 200
    assert response.json()["username"] == unique_user.username

    _refresh_dependency_settings()


def test_proxy_header_auth_user_not_found(api_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PROXY_AUTH_ENABLED", "true")
    monkeypatch.setenv("PROXY_AUTH_HEADER", "Remote-User")
    monkeypatch.setenv("TRUSTED_PROXY", "testclient")
    _refresh_dependency_settings()

    response = api_client.get(api_routes.users_self, headers={"Remote-User": random_string()})
    assert response.status_code == 401

    _refresh_dependency_settings()


def test_proxy_header_auth_disabled_does_not_authenticate(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.delenv("PROXY_AUTH_ENABLED", raising=False)
    monkeypatch.setenv("PROXY_AUTH_HEADER", "Remote-User")
    monkeypatch.setenv("TRUSTED_PROXY", "testclient")
    _refresh_dependency_settings()

    response = api_client.get(api_routes.users_self, headers={"Remote-User": unique_user.username})
    assert response.status_code == 401

    _refresh_dependency_settings()


def test_proxy_header_auth_rejects_wildcard_trusted_proxy(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("PROXY_AUTH_ENABLED", "true")
    monkeypatch.setenv("PROXY_AUTH_HEADER", "Remote-User")
    # Unsafe wildcard should disable proxy auth readiness and fail closed.
    monkeypatch.setenv("TRUSTED_PROXY", "*")
    _refresh_dependency_settings()

    response = api_client.get(api_routes.users_self, headers={"Remote-User": unique_user.username})
    assert response.status_code == 401

    _refresh_dependency_settings()


def test_invalid_token_does_not_fall_back_to_proxy_auth(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("PROXY_AUTH_ENABLED", "true")
    monkeypatch.setenv("PROXY_AUTH_HEADER", "Remote-User")
    monkeypatch.setenv("TRUSTED_PROXY", "testclient")
    _refresh_dependency_settings()

    response = api_client.get(
        api_routes.users_self,
        headers={
            "Authorization": f"Bearer {random_string()}",
            "Remote-User": unique_user.username,
        },
    )
    assert response.status_code == 401

    _refresh_dependency_settings()


def test_valid_token_takes_precedence_over_proxy_header(
    api_client: TestClient, unique_user: TestUser, admin_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("PROXY_AUTH_ENABLED", "true")
    monkeypatch.setenv("PROXY_AUTH_HEADER", "Remote-User")
    monkeypatch.setenv("TRUSTED_PROXY", "testclient")
    _refresh_dependency_settings()

    response = api_client.get(
        api_routes.users_self,
        headers={
            **admin_user.token,
            "Remote-User": unique_user.username,
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == admin_user.username

    _refresh_dependency_settings()


def test_proxy_header_auth_custom_header_existing_user(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("PROXY_AUTH_ENABLED", "true")
    monkeypatch.setenv("PROXY_AUTH_HEADER", "X-Forwarded-User")
    monkeypatch.setenv("TRUSTED_PROXY", "testclient")
    _refresh_dependency_settings()

    response = api_client.get(api_routes.users_self, headers={"X-Forwarded-User": unique_user.username})
    assert response.status_code == 200
    assert response.json()["username"] == unique_user.username

    _refresh_dependency_settings()


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
