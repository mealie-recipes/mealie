import asyncio
import hashlib
import io
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from PIL import Image
from pytest import MonkeyPatch

from mealie.core.config import get_app_settings
from mealie.pkgs.safehttp import ContentTooLargeError, FetchResult
from mealie.pkgs.safehttp.transport import InvalidDomainError
from mealie.schema.user import PrivateUser
from mealie.services.user_services import avatar_service
from tests.utils.fixture_schemas import TestUser

AVATAR_URL = "https://idp.example.com/avatar.png"


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), color="red").save(buffer, format="PNG")
    return buffer.getvalue()


def _result(content: bytes | None = None, content_type: str = "image/png") -> FetchResult:
    return FetchResult(
        content=_png_bytes() if content is None else content,
        status_code=200,
        url=AVATAR_URL,
        headers=httpx.Headers({"content-type": content_type}),
        encoding="utf-8",
    )


def _avatar_path(user_id):
    return PrivateUser.get_directory(user_id) / "profile.webp"


def _reset_avatar_state(user: TestUser) -> PrivateUser:
    """`unique_user` is shared across tests, so clear whatever a previous one stored."""
    return user.repos.users.patch(user.user_id, {"oidc_picture_hash": None})


@pytest.mark.asyncio
async def test_stores_avatar_and_rotates_cache_key(unique_user: TestUser):
    before = _reset_avatar_state(unique_user)

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=_result())) as fetch:
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, AVATAR_URL)

    fetch.assert_awaited_once()
    assert fetch.await_args.kwargs["max_bytes"] == avatar_service.MAX_AVATAR_BYTES

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert _avatar_path(unique_user.user_id).is_file()
    assert after.cache_key != before.cache_key
    assert after.oidc_picture_hash == hashlib.sha256(AVATAR_URL.encode()).hexdigest()


@pytest.mark.asyncio
async def test_unchanged_claim_skips_download(unique_user: TestUser):
    """The whole point of storing the hash: a repeat login must not refetch."""
    unique_user.repos.users.patch(
        unique_user.user_id, {"oidc_picture_hash": hashlib.sha256(AVATAR_URL.encode()).hexdigest()}
    )

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=_result())) as fetch:
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, AVATAR_URL)

    fetch.assert_not_awaited()


@pytest.mark.asyncio
async def test_changed_claim_triggers_download(unique_user: TestUser):
    unique_user.repos.users.patch(unique_user.user_id, {"oidc_picture_hash": "a-different-digest"})

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=_result())) as fetch:
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, AVATAR_URL)

    fetch.assert_awaited_once()


@pytest.mark.parametrize("url", ["http://idp.example.com/a.png", "file:///etc/passwd", "ftp://idp.example.com/a.png"])
@pytest.mark.asyncio
async def test_rejects_non_https_urls(monkeypatch: MonkeyPatch, unique_user: TestUser, url: str):
    monkeypatch.delenv("OIDC_CONFIGURATION_URL", raising=False)
    get_app_settings.cache_clear()

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=_result())) as fetch:
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, url)

    fetch.assert_not_awaited()


@pytest.mark.asyncio
async def test_foreign_host_is_not_allowed_to_reach_private_targets(monkeypatch: MonkeyPatch, unique_user: TestUser):
    """The metadata-endpoint case: a user-supplied URL must not unlock the SSRF guard."""
    monkeypatch.setenv("OIDC_CONFIGURATION_URL", "https://idp.example.com/.well-known/openid-configuration")
    get_app_settings.cache_clear()
    _reset_avatar_state(unique_user)

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=_result())) as fetch:
        await avatar_service.sync_avatar_from_url(
            unique_user.repos.session, unique_user.user_id, "https://169.254.169.254/latest/meta-data/"
        )

    # The fetch is attempted, but without the private-target opt-out, so safehttp's guard blocks it.
    fetch.assert_awaited_once()
    assert fetch.await_args.kwargs["allow_private"] is False


@pytest.mark.asyncio
async def test_self_hosted_idp_on_private_network_is_allowed(monkeypatch: MonkeyPatch, unique_user: TestUser):
    """A self-hosted IdP (Pocket ID et al) serves avatars from a private address over plain HTTP."""
    monkeypatch.setenv("OIDC_CONFIGURATION_URL", "https://pocket-id.lan/.well-known/openid-configuration")
    get_app_settings.cache_clear()
    _reset_avatar_state(unique_user)

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=_result())) as fetch:
        await avatar_service.sync_avatar_from_url(
            unique_user.repos.session, unique_user.user_id, "http://pocket-id.lan/api/users/1/picture"
        )

    fetch.assert_awaited_once()
    assert fetch.await_args.kwargs["allow_private"] is True


@pytest.mark.asyncio
async def test_idp_host_over_https_also_gets_the_opt_out(monkeypatch: MonkeyPatch, unique_user: TestUser):
    monkeypatch.setenv("OIDC_CONFIGURATION_URL", "https://pocket-id.lan/.well-known/openid-configuration")
    get_app_settings.cache_clear()
    _reset_avatar_state(unique_user)

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=_result())) as fetch:
        await avatar_service.sync_avatar_from_url(
            unique_user.repos.session, unique_user.user_id, "https://pocket-id.lan/picture.png"
        )

    fetch.assert_awaited_once()
    assert fetch.await_args.kwargs["allow_private"] is True


@pytest.mark.asyncio
async def test_plain_http_on_a_foreign_host_stays_rejected(monkeypatch: MonkeyPatch, unique_user: TestUser):
    monkeypatch.setenv("OIDC_CONFIGURATION_URL", "https://pocket-id.lan/.well-known/openid-configuration")
    get_app_settings.cache_clear()

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=_result())) as fetch:
        await avatar_service.sync_avatar_from_url(
            unique_user.repos.session, unique_user.user_id, "http://evil.example.com/a.png"
        )

    fetch.assert_not_awaited()


@pytest.mark.asyncio
async def test_no_configured_idp_means_no_opt_out(monkeypatch: MonkeyPatch, unique_user: TestUser):
    monkeypatch.delenv("OIDC_CONFIGURATION_URL", raising=False)
    get_app_settings.cache_clear()
    _reset_avatar_state(unique_user)

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=_result())) as fetch:
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, AVATAR_URL)

    fetch.assert_awaited_once()
    assert fetch.await_args.kwargs["allow_private"] is False


@pytest.mark.parametrize(
    "error",
    [
        InvalidDomainError("invalid request on local resource"),
        ContentTooLargeError("response body exceeds limit"),
        httpx.ConnectError("boom"),
    ],
)
@pytest.mark.asyncio
async def test_swallows_fetch_failures(unique_user: TestUser, error: Exception):
    """A blocked, oversized or simply broken download must never fail the login."""
    before = _reset_avatar_state(unique_user)

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(side_effect=error)):
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, AVATAR_URL)

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.cache_key == before.cache_key
    assert after.oidc_picture_hash is None


@pytest.mark.asyncio
async def test_slow_provider_does_not_stall_login(unique_user: TestUser):
    """A hanging avatar host must not hold the login response open."""
    _reset_avatar_state(unique_user)

    async def _never_finishes(*args, **kwargs):
        await asyncio.sleep(60)

    monkeypatched = patch.object(avatar_service.safehttp, "resilient_fetch", _never_finishes)
    with monkeypatched, patch.object(avatar_service, "AVATAR_FETCH_TIMEOUT", 0.01):
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, AVATAR_URL)

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.oidc_picture_hash is None


@pytest.mark.asyncio
async def test_swallows_empty_response(unique_user: TestUser):
    _reset_avatar_state(unique_user)
    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=None)):
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, AVATAR_URL)

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.oidc_picture_hash is None


@pytest.mark.asyncio
async def test_rejects_non_image_content_type(unique_user: TestUser):
    _reset_avatar_state(unique_user)
    result = _result(content=b"<html>not an image</html>", content_type="text/html")

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=result)):
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, AVATAR_URL)

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.oidc_picture_hash is None


@pytest.mark.asyncio
async def test_swallows_undecodable_image(unique_user: TestUser):
    """Content-Type says image, bytes say otherwise -- Pillow raises and we move on."""
    _reset_avatar_state(unique_user)
    result = _result(content=b"definitely not a png", content_type="image/png")

    with patch.object(avatar_service.safehttp, "resilient_fetch", AsyncMock(return_value=result)):
        await avatar_service.sync_avatar_from_url(unique_user.repos.session, unique_user.user_id, AVATAR_URL)

    after = unique_user.repos.users.get_one(unique_user.user_id)
    assert after is not None
    assert after.oidc_picture_hash is None
