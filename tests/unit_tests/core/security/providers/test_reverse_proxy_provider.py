from pytest import MonkeyPatch

from mealie.core.config import get_app_settings
from mealie.core.security.providers.reverse_proxy_provider import ReverseProxyProvider
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _enable_reverse_proxy_auth(monkeypatch: MonkeyPatch, header: str = "X-Forwarded-User") -> None:
    monkeypatch.setenv("REVERSE_PROXY_AUTH_ENABLED", "true")
    monkeypatch.setenv("REVERSE_PROXY_AUTH_HEADER", header)
    get_app_settings.cache_clear()


def test_no_username(monkeypatch: MonkeyPatch):
    _enable_reverse_proxy_auth(monkeypatch)
    auth_provider = ReverseProxyProvider(None, "")
    assert auth_provider.authenticate() is None


def test_authenticates_existing_user(monkeypatch: MonkeyPatch, unique_user: TestUser):
    _enable_reverse_proxy_auth(monkeypatch)
    auth_provider = ReverseProxyProvider(unique_user.repos.session, unique_user.username)
    assert auth_provider.authenticate() is not None


def test_authenticates_existing_user_by_email(monkeypatch: MonkeyPatch, unique_user: TestUser):
    _enable_reverse_proxy_auth(monkeypatch)
    auth_provider = ReverseProxyProvider(unique_user.repos.session, unique_user.email)
    assert auth_provider.authenticate() is not None


def test_creates_new_user_when_signup_enabled(monkeypatch: MonkeyPatch, unique_user: TestUser):
    _enable_reverse_proxy_auth(monkeypatch)
    monkeypatch.setenv("REVERSE_PROXY_AUTH_SIGNUP_ENABLED", "true")
    get_app_settings.cache_clear()

    username = random_string(10)
    auth_provider = ReverseProxyProvider(unique_user.repos.session, username)
    assert auth_provider.authenticate() is not None

    repos = get_repositories(unique_user.repos.session, group_id=None, household_id=None)
    created_user = repos.users.get_one(username, "username", any_case=True)
    assert created_user is not None
    assert created_user.auth_method == AuthMethod.REVERSE_PROXY


def test_does_not_create_new_user_when_signup_disabled(monkeypatch: MonkeyPatch, unique_user: TestUser):
    _enable_reverse_proxy_auth(monkeypatch)
    monkeypatch.setenv("REVERSE_PROXY_AUTH_SIGNUP_ENABLED", "false")
    get_app_settings.cache_clear()

    username = random_string(10)
    auth_provider = ReverseProxyProvider(unique_user.repos.session, username)
    assert auth_provider.authenticate() is None
