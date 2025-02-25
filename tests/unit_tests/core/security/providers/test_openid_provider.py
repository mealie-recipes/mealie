import pytest
from pytest import MonkeyPatch, Session
import logging

from mealie.core.config import get_app_settings
from mealie.core.security.providers.openid_provider import OpenIDProvider
from mealie.repos.all_repositories import get_repositories
from tests.utils.factories import random_email, random_string
from tests.utils.fixture_schemas import TestUser


def test_no_claims():
    auth_provider = OpenIDProvider(None, None)

    assert auth_provider.authenticate() is None


def test_empty_claims():
    auth_provider = OpenIDProvider(None, {})

    assert auth_provider.authenticate() is None


def test_empty_required_claims():
    data = {
        "preferred_username": "dude1",
        "email": "",  # Empty required claim
        "name": "Firstname Lastname",
        "groups": ["mealie_user"],
    }
    auth_provider = OpenIDProvider(None, data)

    assert auth_provider.authenticate() is None


def test_missing_claims():
    data = {"preferred_username": "dude1"}
    auth_provider = OpenIDProvider(None, data)

    assert auth_provider.authenticate() is None


def test_missing_groups_claim(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": "email@email.com",
        "name": "Firstname Lastname",
    }
    auth_provider = OpenIDProvider(None, data)

    assert auth_provider.authenticate() is None


def test_missing_user_group(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": "email@email.com",
        "name": "Firstname Lastname",
        "groups": ["not_mealie_user"],
    }
    auth_provider = OpenIDProvider(None, data)

    assert auth_provider.authenticate() is None


def test_has_user_group_existing_user(monkeypatch: MonkeyPatch, unique_user: TestUser):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": unique_user.email,
        "name": "Firstname Lastname",
        "groups": ["mealie_user"],
    }
    auth_provider = OpenIDProvider(unique_user.repos.session, data)

    assert auth_provider.authenticate() is not None


def test_has_admin_group_existing_user(monkeypatch: MonkeyPatch, unique_user: TestUser):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    monkeypatch.setenv("OIDC_ADMIN_GROUP", "mealie_admin")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": unique_user.email,
        "name": "Firstname Lastname",
        "groups": ["mealie_admin"],
    }
    auth_provider = OpenIDProvider(unique_user.repos.session, data)

    assert auth_provider.authenticate() is not None


def test_has_user_group_new_user(monkeypatch: MonkeyPatch, session: Session):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    monkeypatch.setenv("OIDC_ADMIN_GROUP", "mealie_admin")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": "dude1@email.com",
        "name": "Firstname Lastname",
        "groups": ["mealie_user"],
    }
    auth_provider = OpenIDProvider(session, data)

    assert auth_provider.authenticate() is not None

    db = get_repositories(session, group_id=None, household_id=None)
    user = db.users.get_one("dude1", "username")
    assert user is not None
    assert not user.admin


def test_has_admin_group_new_user(monkeypatch: MonkeyPatch, session: Session):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    monkeypatch.setenv("OIDC_ADMIN_GROUP", "mealie_admin")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude2",
        "email": "dude2@email.com",
        "name": "Firstname Lastname",
        "groups": ["mealie_admin"],
    }
    auth_provider = OpenIDProvider(session, data)

    assert auth_provider.authenticate() is not None

    db = get_repositories(session, group_id=None, household_id=None)
    user = db.users.get_one("dude2", "username")
    assert user is not None
    assert user.admin


@pytest.mark.parametrize("valid_group", [True, False])
@pytest.mark.parametrize("valid_household", [True, False])
def test_ldap_user_creation_invalid_group_or_household(
    monkeypatch: MonkeyPatch, session: Session, valid_group: bool, valid_household: bool
):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    monkeypatch.setenv("OIDC_ADMIN_GROUP", "mealie_admin")
    if not valid_group:
        monkeypatch.setenv("DEFAULT_GROUP", random_string())
    if not valid_household:
        monkeypatch.setenv("DEFAULT_HOUSEHOLD", random_string())
    get_app_settings.cache_clear()

    data = {
        "preferred_username": random_string(),
        "email": random_email(),
        "name": random_string(),
        "groups": ["mealie_user"],
    }
    auth_provider = OpenIDProvider(session, data)

    if valid_group and valid_household:
        assert auth_provider.authenticate() is not None
    else:
        assert auth_provider.authenticate() is None

    db = get_repositories(session, group_id=None, household_id=None)
    user = db.users.get_one(data["preferred_username"], "username")

    if valid_group and valid_household:
        assert user is not None
    else:
        assert user is None


def test_claims_logging(caplog, session: Session):
    caplog.set_level(logging.DEBUG)
    data = {
        "preferred_username": "testuser",
        "email": "test@example.com",
        "name": "Test User",
        "groups": ["mealie_user"],
    }
    auth_provider = OpenIDProvider(session, data)
    auth_provider.authenticate()

    # Verify that all claims are logged
    for key, value in data.items():
        assert f"{key}: {value}" in caplog.text
