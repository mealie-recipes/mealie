import hashlib
import io
import logging
import socket
from unittest.mock import MagicMock

import pytest
import requests
from PIL import Image
from pytest import MonkeyPatch, Session

from mealie.core.config import get_app_settings
from mealie.core.exceptions import MissingClaimException
from mealie.core.security.providers import openid_provider
from mealie.core.security.providers.openid_provider import OpenIDProvider
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user import PrivateUser
from tests.utils.factories import random_email, random_string
from tests.utils.fixture_schemas import TestUser


def test_no_claims():
    auth_provider = OpenIDProvider(None, None)

    with pytest.raises(MissingClaimException):
        auth_provider.authenticate()


def test_empty_claims():
    auth_provider = OpenIDProvider(None, {})

    with pytest.raises(MissingClaimException):
        auth_provider.authenticate()


def test_empty_required_claims():
    data = {
        "preferred_username": "dude1",
        "email": "",  # Empty required claim
        "name": "Firstname Lastname",
        "groups": ["mealie_user"],
    }
    auth_provider = OpenIDProvider(None, data)

    with pytest.raises(MissingClaimException):
        auth_provider.authenticate()


def test_missing_claims():
    data = {"preferred_username": "dude1"}
    auth_provider = OpenIDProvider(None, data)

    with pytest.raises(MissingClaimException):
        auth_provider.authenticate()


def test_missing_groups_claim(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": "email@email.com",
        "email_verified": True,
        "name": "Firstname Lastname",
    }
    auth_provider = OpenIDProvider(None, data)

    with pytest.raises(MissingClaimException):
        auth_provider.authenticate()


def test_missing_groups_claim_admin(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("OIDC_ADMIN_GROUP", "mealie_admin")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": "email@email.com",
        "email_verified": True,
        "name": "Firstname Lastname",
    }
    auth_provider = OpenIDProvider(None, data)

    with pytest.raises(MissingClaimException):
        auth_provider.authenticate()


def test_missing_groups_claim_with_default(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": "email@email.com",
        "email_verified": True,
        "name": "Firstname Lastname",
    }
    auth_provider = OpenIDProvider(None, data, True)

    assert auth_provider.authenticate() is None


def test_missing_groups_claim_admin_group_with_default(monkeypatch: MonkeyPatch, unique_user: TestUser):
    monkeypatch.setenv("OIDC_ADMIN_GROUP", "mealie_admin")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": unique_user.email,
        "email_verified": True,
        "name": "Firstname Lastname",
    }
    auth_provider = OpenIDProvider(unique_user.repos.session, data, True)

    assert auth_provider.authenticate() is not None


def test_missing_user_group(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("OIDC_USER_GROUP", "mealie_user")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": "dude1",
        "email": "email@email.com",
        "email_verified": True,
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
        "email_verified": True,
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
        "email_verified": True,
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
        "email_verified": True,
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
        "email_verified": True,
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
        "email_verified": True,
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


def test_rejects_unverified_email(monkeypatch: MonkeyPatch, session: Session):
    monkeypatch.setenv("OIDC_REQUIRES_EMAIL_VERIFICATION", "true")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": random_string(),
        "email": random_email(),
        "email_verified": False,
        "name": random_string(),
    }
    auth_provider = OpenIDProvider(session, data)

    with pytest.raises(MissingClaimException):
        auth_provider.authenticate()


def test_rejects_missing_email_verified(monkeypatch: MonkeyPatch, session: Session):
    monkeypatch.setenv("OIDC_REQUIRES_EMAIL_VERIFICATION", "true")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": random_string(),
        "email": random_email(),
        "name": random_string(),
    }
    auth_provider = OpenIDProvider(session, data)

    with pytest.raises(MissingClaimException):
        auth_provider.authenticate()


def test_does_not_adopt_existing_account_with_unverified_email(monkeypatch: MonkeyPatch, unique_user: TestUser):
    """An unverified email must not be able to log into (take over) an existing account."""
    monkeypatch.setenv("OIDC_REQUIRES_EMAIL_VERIFICATION", "true")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": random_string(),
        "email": unique_user.email,
        "email_verified": False,
        "name": random_string(),
    }
    auth_provider = OpenIDProvider(unique_user.repos.session, data)

    with pytest.raises(MissingClaimException):
        auth_provider.authenticate()


def test_adopts_existing_account_with_verified_email(monkeypatch: MonkeyPatch, unique_user: TestUser):
    """A verified email legitimately links to an existing (non-OIDC) account."""
    monkeypatch.setenv("OIDC_REQUIRES_EMAIL_VERIFICATION", "true")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": random_string(),
        "email": unique_user.email,
        "email_verified": True,
        "name": random_string(),
    }
    auth_provider = OpenIDProvider(unique_user.repos.session, data)

    assert auth_provider.authenticate() is not None


def test_allows_unverified_email_when_verification_disabled(monkeypatch: MonkeyPatch, session: Session):
    monkeypatch.setenv("OIDC_REQUIRES_EMAIL_VERIFICATION", "false")
    get_app_settings.cache_clear()

    data = {
        "preferred_username": random_string(),
        "email": random_email(),
        "name": random_string(),
    }
    auth_provider = OpenIDProvider(session, data)

    assert auth_provider.authenticate() is not None


def test_claims_logging(monkeypatch: MonkeyPatch, caplog, session: Session):
    monkeypatch.setenv("OIDC_REQUIRES_EMAIL_VERIFICATION", "true")
    get_app_settings.cache_clear()
    caplog.set_level(logging.DEBUG)
    data = {
        "preferred_username": "testuser",
        "email": "test@example.com",
        "email_verified": True,
        "name": "Test User",
        "groups": ["mealie_user"],
    }
    auth_provider = OpenIDProvider(session, data)
    auth_provider.authenticate()

    # Verify that all claims are logged
    for key, value in data.items():
        assert f"{key}: {value}" in caplog.text


# ---------------------------------------------------------------------------
# Profile image from the `picture` claim
# ---------------------------------------------------------------------------
PICTURE_URL = "https://idp.example.com/avatar.png"


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), color="red").save(buffer, format="PNG")
    return buffer.getvalue()


class _FakeResponse:
    def __init__(self, body: bytes, headers: dict | None = None):
        self.headers = headers or {}
        self._body = body

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int = 8192):
        for i in range(0, len(self._body), chunk_size):
            yield self._body[i : i + chunk_size]


def _picture_claims(picture: object = None) -> dict:
    data = {
        "preferred_username": random_string(),
        "email": random_email(),
        "email_verified": True,
        "name": random_string(),
    }
    if picture is not None:
        data["picture"] = picture
    return data


def _resolve_to(monkeypatch: MonkeyPatch, address: str) -> None:
    """Pins DNS resolution so the guard's decision is deterministic and offline."""
    monkeypatch.setattr(
        openid_provider.socket,
        "getaddrinfo",
        lambda host, port, *a, **kw: [(None, None, None, "", (address, 0))],
    )


@pytest.fixture
def _oidc_env(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("OIDC_REQUIRES_EMAIL_VERIFICATION", "true")
    monkeypatch.setenv("OIDC_CONFIGURATION_URL", "https://idp.example.com/.well-known/openid-configuration")
    get_app_settings.cache_clear()
    yield
    get_app_settings.cache_clear()


def test_stores_picture_and_rotates_cache_key(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    _resolve_to(monkeypatch, "93.184.216.34")
    before = unique_user.repos.users.patch(unique_user.user_id, {"oidc_picture_hash": None})

    url = "https://cdn.example.com/avatar.png"
    fake_get = MagicMock(return_value=_FakeResponse(_png_bytes()))
    monkeypatch.setattr(openid_provider.requests, "get", fake_get)

    data = _picture_claims(url)
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    fake_get.assert_called_once()
    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert (PrivateUser.get_directory(unique_user.user_id) / "profile.webp").is_file()
    assert after.cache_key != before.cache_key
    assert after.oidc_picture_hash == hashlib.sha256(url.encode()).hexdigest()


def test_unchanged_picture_claim_skips_download(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """Genson's point: a repeat login must not refetch an image that hasn't changed."""
    _resolve_to(monkeypatch, "93.184.216.34")
    url = "https://cdn.example.com/avatar.png"
    unique_user.repos.users.patch(unique_user.user_id, {"oidc_picture_hash": hashlib.sha256(url.encode()).hexdigest()})

    fake_get = MagicMock(return_value=_FakeResponse(_png_bytes()))
    monkeypatch.setattr(openid_provider.requests, "get", fake_get)

    data = _picture_claims(url)
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    fake_get.assert_not_called()


@pytest.mark.parametrize("picture", [None, 123, {"url": PICTURE_URL}, ""])
def test_absent_or_non_string_picture_claim(_oidc_env, monkeypatch: MonkeyPatch, session: Session, picture):
    fake_get = MagicMock()
    monkeypatch.setattr(openid_provider.requests, "get", fake_get)

    assert OpenIDProvider(session, _picture_claims(picture)).authenticate() is not None
    fake_get.assert_not_called()


@pytest.mark.parametrize(
    "url",
    [
        "http://cdn.example.com/a.png",  # plain HTTP on a foreign host
        "file:///etc/passwd",
        "ftp://cdn.example.com/a.png",
        "not-a-url",
    ],
)
def test_rejects_urls_that_are_not_https(_oidc_env, monkeypatch: MonkeyPatch, session: Session, url: str):
    _resolve_to(monkeypatch, "93.184.216.34")
    fake_get = MagicMock()
    monkeypatch.setattr(openid_provider.requests, "get", fake_get)

    assert OpenIDProvider(session, _picture_claims(url)).authenticate() is not None
    fake_get.assert_not_called()


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",  # loopback
        "10.0.0.5",  # private
        "192.168.1.10",  # private
        "169.254.169.254",  # link-local / cloud metadata
        "::1",
        "fd00::1",
    ],
)
def test_rejects_non_public_addresses(_oidc_env, monkeypatch: MonkeyPatch, session: Session, address: str):
    """No request is made at all -- the guard runs before `requests.get`."""
    _resolve_to(monkeypatch, address)
    fake_get = MagicMock()
    monkeypatch.setattr(openid_provider.requests, "get", fake_get)

    assert OpenIDProvider(session, _picture_claims("https://cdn.example.com/a.png")).authenticate() is not None
    fake_get.assert_not_called()


def test_unresolvable_host_is_rejected(_oidc_env, monkeypatch: MonkeyPatch, session: Session):
    def _boom(*args, **kwargs):
        raise socket.gaierror("no such host")

    monkeypatch.setattr(openid_provider.socket, "getaddrinfo", _boom)
    fake_get = MagicMock()
    monkeypatch.setattr(openid_provider.requests, "get", fake_get)

    assert OpenIDProvider(session, _picture_claims("https://nope.example.com/a.png")).authenticate() is not None
    fake_get.assert_not_called()


@pytest.mark.parametrize("url", ["https://idp.example.com/pic.png", "http://idp.example.com/pic.png"])
def test_provider_own_host_is_allowed_on_a_private_network(
    _oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser, url: str
):
    """A self-hosted IdP sits on the LAN, so its own avatars must stay reachable."""
    _resolve_to(monkeypatch, "192.168.1.10")
    unique_user.repos.users.patch(unique_user.user_id, {"oidc_picture_hash": None})

    fake_get = MagicMock(return_value=_FakeResponse(_png_bytes()))
    monkeypatch.setattr(openid_provider.requests, "get", fake_get)

    data = _picture_claims(url)
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    fake_get.assert_called_once()


def test_oversized_declared_content_length_is_refused(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    _resolve_to(monkeypatch, "93.184.216.34")
    unique_user.repos.users.patch(unique_user.user_id, {"oidc_picture_hash": None})

    too_big = str(openid_provider.MAX_PICTURE_BYTES + 1)
    response = _FakeResponse(_png_bytes(), headers={"content-length": too_big})
    monkeypatch.setattr(openid_provider.requests, "get", MagicMock(return_value=response))

    data = _picture_claims("https://cdn.example.com/huge.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.oidc_picture_hash is None


def test_oversized_stream_is_refused(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """A server that lies about (or omits) Content-Length is caught while streaming."""
    _resolve_to(monkeypatch, "93.184.216.34")
    unique_user.repos.users.patch(unique_user.user_id, {"oidc_picture_hash": None})

    body = b"x" * (openid_provider.MAX_PICTURE_BYTES + 1)
    response = _FakeResponse(body, headers={"content-length": "10"})
    monkeypatch.setattr(openid_provider.requests, "get", MagicMock(return_value=response))

    data = _picture_claims("https://cdn.example.com/liar.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.oidc_picture_hash is None


def test_failed_download_does_not_break_login(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    _resolve_to(monkeypatch, "93.184.216.34")
    before = unique_user.repos.users.patch(unique_user.user_id, {"oidc_picture_hash": None})

    monkeypatch.setattr(openid_provider.requests, "get", MagicMock(side_effect=requests.ConnectionError("boom")))

    data = _picture_claims("https://cdn.example.com/a.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.cache_key == before.cache_key
    assert after.oidc_picture_hash is None


def test_undecodable_image_does_not_break_login(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    _resolve_to(monkeypatch, "93.184.216.34")
    unique_user.repos.users.patch(unique_user.user_id, {"oidc_picture_hash": None})

    response = _FakeResponse(b"definitely not a png")
    monkeypatch.setattr(openid_provider.requests, "get", MagicMock(return_value=response))

    data = _picture_claims("https://cdn.example.com/a.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.oidc_picture_hash is None
