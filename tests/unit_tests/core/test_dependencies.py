import pytest
from starlette.requests import Request

from mealie.core.dependencies.dependencies import get_auth_token


def build_request(cookie: str | None = None) -> Request:
    headers = [(b"cookie", cookie.encode())] if cookie else []
    return Request({"type": "http", "headers": headers})


@pytest.mark.asyncio
async def test_auth_token_comes_from_the_authorization_header():
    token = await get_auth_token(build_request(), "from-header")

    assert token == "from-header"


@pytest.mark.asyncio
async def test_auth_token_falls_back_to_the_session_cookie():
    """Downloads and exports opened outside the SPA carry no Authorization header, only the cookie."""
    token = await get_auth_token(build_request("mealie.access_token=from-cookie"), None)

    assert token == "from-cookie"


@pytest.mark.asyncio
async def test_authorization_header_wins_over_the_cookie():
    """A caller who bothered to send a header meant that credential, however stale the cookie is."""
    token = await get_auth_token(build_request("mealie.access_token=from-cookie"), "from-header")

    assert token == "from-header"


@pytest.mark.asyncio
async def test_unrelated_cookies_are_ignored():
    token = await get_auth_token(build_request("some_other_cookie=nope"), None)

    assert token == ""


@pytest.mark.asyncio
async def test_no_credential_yields_an_empty_token():
    token = await get_auth_token(build_request(), None)

    assert token == ""
