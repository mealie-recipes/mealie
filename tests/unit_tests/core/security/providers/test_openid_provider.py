import hashlib
import io
import logging
import socket
from pathlib import Path

import httpx
import pytest
from PIL import Image
from pytest import MonkeyPatch, Session

from mealie.core.config import get_app_settings
from mealie.core.exceptions import MissingClaimException
from mealie.core.security.providers import openid_provider
from mealie.core.security.providers.openid_provider import OpenIDProvider
from mealie.pkgs.safehttp import transport as safehttp_transport
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


def _response(body: bytes, headers: dict | None = None, status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code, headers=headers or {}, content=body)


def _redirect(location: str, status_code: int = 302) -> httpx.Response:
    return _response(b"", headers={"location": location}, status_code=status_code)


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
    _resolve_hosts(monkeypatch, {}, default=address)


def _resolve_hosts(monkeypatch: MonkeyPatch, mapping: dict[str, str], default: str = "93.184.216.34") -> None:
    """
    Per-host DNS pinning, so a redirect chain can cross from a public host to a private one.

    The vetting now happens inside `safehttp`, so this patches the resolver that layer uses.
    """
    monkeypatch.setattr(
        safehttp_transport.socket,
        "getaddrinfo",
        lambda host, port, *a, **kw: [(None, None, None, "", (mapping.get(host, default), 0))],
    )


def _patch_network(monkeypatch: MonkeyPatch, responses: list) -> list[str]:
    """
    Scripts consecutive transport responses and records the URLs actually requested.

    This stubs the curl transport underneath `SafeTransport`, so the real SSRF vetting and
    connection pinning still run on every hop -- only the socket work is replaced. An entry may
    be an exception, which is raised instead of returned.
    """
    requested: list[str] = []
    queue = list(responses)

    def fake_handle_request(_self, request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        if not queue:
            raise AssertionError(f"unexpected request to {request.url}")
        response = queue.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(safehttp_transport.CurlTransport, "handle_request", fake_handle_request)
    return requested


@pytest.fixture
def _oidc_env(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("OIDC_REQUIRES_EMAIL_VERIFICATION", "true")
    monkeypatch.setenv("OIDC_CONFIGURATION_URL", "https://idp.example.com/.well-known/openid-configuration")
    get_app_settings.cache_clear()
    yield
    get_app_settings.cache_clear()


def test_stores_picture_and_rotates_cache_key(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    _resolve_to(monkeypatch, "93.184.216.34")
    before = unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    url = "https://cdn.example.com/avatar.png"
    requested = _patch_network(monkeypatch, [_response(_png_bytes())])

    data = _picture_claims(url)
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    assert requested == [url]
    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert (PrivateUser.get_directory(unique_user.user_id) / "profile.webp").is_file()
    assert after.cache_key != before.cache_key
    assert after.external_avatar_hash == hashlib.sha256(url.encode()).hexdigest()


def test_unchanged_picture_claim_skips_download(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """Genson's point: a repeat login must not refetch an image that hasn't changed."""
    _resolve_to(monkeypatch, "93.184.216.34")
    url = "https://cdn.example.com/avatar.png"
    unique_user.repos.users.patch(
        unique_user.user_id, {"external_avatar_hash": hashlib.sha256(url.encode()).hexdigest()}
    )

    requested = _patch_network(monkeypatch, [_response(_png_bytes())])

    data = _picture_claims(url)
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    assert requested == []


@pytest.mark.parametrize("picture", [None, 123, {"url": PICTURE_URL}, ""])
def test_absent_or_non_string_picture_claim(_oidc_env, monkeypatch: MonkeyPatch, session: Session, picture):
    requested = _patch_network(monkeypatch, [])

    assert OpenIDProvider(session, _picture_claims(picture)).authenticate() is not None
    assert requested == []


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
    requested = _patch_network(monkeypatch, [])

    assert OpenIDProvider(session, _picture_claims(url)).authenticate() is not None
    assert requested == []


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",  # loopback
        "10.0.0.5",  # private
        "192.168.1.10",  # private
        "169.254.169.254",  # link-local / cloud metadata
        "100.64.0.1",  # CGNAT
        "::1",
        "fd00::1",
        "::ffff:127.0.0.1",  # IPv4-mapped loopback
    ],
)
def test_rejects_non_public_addresses(_oidc_env, monkeypatch: MonkeyPatch, session: Session, address: str):
    """No connection is made at all -- `safehttp` rejects before it reaches the socket."""
    _resolve_to(monkeypatch, address)
    requested = _patch_network(monkeypatch, [])

    assert OpenIDProvider(session, _picture_claims("https://cdn.example.com/a.png")).authenticate() is not None
    assert requested == []


def test_unresolvable_host_is_rejected(_oidc_env, monkeypatch: MonkeyPatch, session: Session):
    def _boom(*args, **kwargs):
        raise socket.gaierror("no such host")

    monkeypatch.setattr(safehttp_transport.socket, "getaddrinfo", _boom)
    requested = _patch_network(monkeypatch, [])

    assert OpenIDProvider(session, _picture_claims("https://nope.example.com/a.png")).authenticate() is not None
    assert requested == []


def test_disallow_list_blocks_a_public_avatar_host(monkeypatch: MonkeyPatch, session: Session):
    """`HTTP_DISALLOW_LIST` reaches the avatar fetch like any other server-initiated request."""
    monkeypatch.setenv("OIDC_REQUIRES_EMAIL_VERIFICATION", "true")
    monkeypatch.setenv("OIDC_CONFIGURATION_URL", "https://idp.example.com/.well-known/openid-configuration")
    monkeypatch.setenv("HTTP_DISALLOW_LIST", "cdn.example.com")
    get_app_settings.cache_clear()

    try:
        _resolve_to(monkeypatch, "93.184.216.34")
        requested = _patch_network(monkeypatch, [])

        assert OpenIDProvider(session, _picture_claims("https://cdn.example.com/a.png")).authenticate() is not None
        assert requested == []
    finally:
        get_app_settings.cache_clear()


@pytest.mark.parametrize("url", ["https://idp.example.com/pic.png", "http://idp.example.com/pic.png"])
def test_provider_own_host_is_allowed_on_a_private_network(
    _oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser, url: str
):
    """A self-hosted IdP sits on the LAN, so its own avatars must stay reachable."""
    _resolve_to(monkeypatch, "192.168.1.10")
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    requested = _patch_network(monkeypatch, [_response(_png_bytes())])

    data = _picture_claims(url)
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    assert requested == [url]


def test_oversized_declared_content_length_is_refused(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    _resolve_to(monkeypatch, "93.184.216.34")
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    too_big = str(openid_provider.MAX_PICTURE_BYTES + 1)
    _patch_network(monkeypatch, [_response(_png_bytes(), headers={"content-length": too_big})])

    data = _picture_claims("https://cdn.example.com/huge.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.external_avatar_hash is None


def test_oversized_stream_is_refused(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """A server that lies about (or omits) Content-Length is caught while streaming."""
    _resolve_to(monkeypatch, "93.184.216.34")
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    body = b"x" * (openid_provider.MAX_PICTURE_BYTES + 1)
    _patch_network(monkeypatch, [_response(body, headers={"content-length": "10"})])

    data = _picture_claims("https://cdn.example.com/liar.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.external_avatar_hash is None


def test_failed_download_does_not_break_login(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    _resolve_to(monkeypatch, "93.184.216.34")
    before = unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    _patch_network(monkeypatch, [httpx.ConnectError("boom")])

    data = _picture_claims("https://cdn.example.com/a.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.cache_key == before.cache_key
    assert after.external_avatar_hash is None


def test_error_status_does_not_break_login(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """`raise_for_status` still guards the body, now through httpx."""
    _resolve_to(monkeypatch, "93.184.216.34")
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    _patch_network(monkeypatch, [_response(b"nope", status_code=404)])

    data = _picture_claims("https://cdn.example.com/a.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.external_avatar_hash is None


def test_undecodable_image_does_not_break_login(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    _resolve_to(monkeypatch, "93.184.216.34")
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    _patch_network(monkeypatch, [_response(b"definitely not a png")])

    data = _picture_claims("https://cdn.example.com/a.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.external_avatar_hash is None


def _authenticate_with_picture(user: TestUser, url: str):
    data = _picture_claims(url)
    data["email"] = user.email
    return OpenIDProvider(user.repos.session, data).authenticate()


@pytest.mark.parametrize("status_code", [301, 302, 303, 307, 308])
def test_follows_redirect_to_a_vetted_host(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser, status_code):
    """httpx walks the chain, but every hop re-enters the transport and is vetted again."""
    _resolve_hosts(monkeypatch, {})  # everything public
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    requested = _patch_network(
        monkeypatch,
        [_redirect("https://cdn2.example.com/real.png", status_code), _response(_png_bytes())],
    )

    assert _authenticate_with_picture(unique_user, "https://cdn.example.com/a.png") is not None

    assert requested == ["https://cdn.example.com/a.png", "https://cdn2.example.com/real.png"]
    assert (PrivateUser.get_directory(unique_user.user_id) / "profile.webp").is_file()


def test_refuses_redirect_to_a_private_address(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """The case Genson was worried about: hop one is public, hop two points inward."""
    _resolve_hosts(monkeypatch, {"metadata.internal": "169.254.169.254"})
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    requested = _patch_network(monkeypatch, [_redirect("https://metadata.internal/latest/meta-data/")])

    assert _authenticate_with_picture(unique_user, "https://cdn.example.com/a.png") is not None

    # The redirect target is never connected to.
    assert requested == ["https://cdn.example.com/a.png"]
    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.external_avatar_hash is None


def test_refuses_redirect_downgrading_to_http(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """httpx would follow a downgrade on its own, so the scheme is re-checked per hop."""
    _resolve_hosts(monkeypatch, {})
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    requested = _patch_network(monkeypatch, [_redirect("http://cdn2.example.com/a.png")])

    assert _authenticate_with_picture(unique_user, "https://cdn.example.com/a.png") is not None

    assert requested == ["https://cdn.example.com/a.png"]
    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.external_avatar_hash is None


def test_relative_location_is_resolved_against_the_current_url(
    _oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser
):
    """A Location may be relative (RFC 9110); treating it as absolute would break the check."""
    _resolve_hosts(monkeypatch, {})
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    requested = _patch_network(monkeypatch, [_redirect("/avatars/real.png"), _response(_png_bytes())])

    assert _authenticate_with_picture(unique_user, "https://cdn.example.com/users/1/a.png") is not None

    assert requested == [
        "https://cdn.example.com/users/1/a.png",
        "https://cdn.example.com/avatars/real.png",
    ]


def test_redirect_chain_is_capped(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """A loop must terminate rather than spin."""
    _resolve_hosts(monkeypatch, {})
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    hops = openid_provider.MAX_PICTURE_REDIRECTS + 2
    requested = _patch_network(monkeypatch, [_redirect(f"https://cdn.example.com/{i}.png") for i in range(hops)])

    assert _authenticate_with_picture(unique_user, "https://cdn.example.com/a.png") is not None

    assert len(requested) == openid_provider.MAX_PICTURE_REDIRECTS + 1
    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.external_avatar_hash is None


def test_redirect_without_location_is_refused(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """A 302 whose Location is empty resolves back to itself, so it must hit the cap and stop."""
    _resolve_hosts(monkeypatch, {})
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    hops = openid_provider.MAX_PICTURE_REDIRECTS + 2
    requested = _patch_network(monkeypatch, [_redirect("") for _ in range(hops)])

    assert _authenticate_with_picture(unique_user, "https://cdn.example.com/a.png") is not None

    assert len(requested) == openid_provider.MAX_PICTURE_REDIRECTS + 1
    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.external_avatar_hash is None


def test_temp_file_is_moved_not_left_behind(_oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser):
    """`shutil.move` leaves no copy behind in the temp directory."""
    _resolve_to(monkeypatch, "93.184.216.34")
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    moved: list[tuple] = []
    real_move = openid_provider.shutil.move
    monkeypatch.setattr(
        openid_provider.shutil,
        "move",
        lambda src, dst: (moved.append((src, dst)), real_move(src, dst))[1],
    )
    _patch_network(monkeypatch, [_response(_png_bytes())])

    data = _picture_claims("https://cdn.example.com/a.png")
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    assert len(moved) == 1
    source, _ = moved[0]
    assert not Path(source).exists()
    assert (PrivateUser.get_directory(unique_user.user_id) / "profile.webp").is_file()


@pytest.mark.parametrize(
    "picture",
    [
        "https://[::1",  # malformed IPv6 literal -- urlparse raises ValueError
        "https://" + "a" * 300 + ".com/a.png",  # over-long label -- getaddrinfo raises UnicodeError
    ],
)
def test_malformed_picture_claim_does_not_break_login(
    _oidc_env, monkeypatch: MonkeyPatch, unique_user: TestUser, picture: str
):
    """A claim that trips up parsing or resolution must skip the avatar, not fail the login."""
    unique_user.repos.users.patch(unique_user.user_id, {"external_avatar_hash": None})

    requested = _patch_network(monkeypatch, [])

    data = _picture_claims(picture)
    data["email"] = unique_user.email
    assert OpenIDProvider(unique_user.repos.session, data).authenticate() is not None

    assert requested == []
    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.external_avatar_hash is None
