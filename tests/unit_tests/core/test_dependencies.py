from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from mealie.core.dependencies.dependencies import get_auth_token, validate_long_live_token


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


class FakeSession:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class FakeApiTokenRepo:
    def __init__(self, tokens):
        self.tokens = tokens
        self.query = None

    def multi_query(self, query):
        self.query = query
        return self.tokens


def test_validate_long_live_token_commits_after_successful_lookup(monkeypatch):
    session = FakeSession()
    user = SimpleNamespace(id="user-id")
    api_tokens = FakeApiTokenRepo([SimpleNamespace(user=user)])

    monkeypatch.setattr(
        "mealie.core.dependencies.dependencies.get_repositories",
        lambda session, group_id, household_id: SimpleNamespace(api_tokens=api_tokens),
    )

    assert validate_long_live_token(session, "client-token", "user-id") is user
    assert api_tokens.query == {"token": "client-token", "user_id": "user-id"}
    assert session.committed is True
    assert session.rolled_back is False


def test_validate_long_live_token_rolls_back_after_failed_lookup(monkeypatch):
    session = FakeSession()
    api_tokens = FakeApiTokenRepo([])

    monkeypatch.setattr(
        "mealie.core.dependencies.dependencies.get_repositories",
        lambda session, group_id, household_id: SimpleNamespace(api_tokens=api_tokens),
    )

    with pytest.raises(HTTPException):
        validate_long_live_token(session, "client-token", "user-id")

    assert session.committed is False
    assert session.rolled_back is True
