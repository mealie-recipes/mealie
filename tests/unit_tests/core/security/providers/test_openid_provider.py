from pytest import MonkeyPatch, Session

from mealie.core.config import get_app_settings
from mealie.core.security.providers.openid_provider import OpenIDProvider
from mealie.repos.all_repositories import get_repositories
from tests.utils.fixture_schemas import TestUser


def test_no_claims():
    auth_provider = OpenIDProvider(None, None)

    assert auth_provider.authenticate() is None


def test_empty_claims():
    auth_provider = OpenIDProvider(None, {})

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
