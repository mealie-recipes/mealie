from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from authlib.integrations.base_client.async_openid import AsyncOpenIDMixin
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from mealie.core.security.providers import openid_provider
from mealie.routes.auth import auth as auth_routes
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser

END_SESSION_ENDPOINT = "https://idp.example/logout"
ID_TOKEN_COOKIE = auth_routes.OIDC_ID_TOKEN_COOKIE_NAME


class OAuthClientMock:
    """Stands in for the authlib OIDC client"""

    client_id = "client-id"

    def __init__(self, metadata: dict | None = None, metadata_error: Exception | None = None):
        self.metadata = {"end_session_endpoint": END_SESSION_ENDPOINT} if metadata is None else metadata
        self.metadata_error = metadata_error

    async def load_server_metadata(self) -> dict:
        if self.metadata_error:
            raise self.metadata_error
        return self.metadata

    async def create_logout_url(self, **kwargs) -> dict:
        # authlib's own implementation, so the tests check the URL it really builds
        return await AsyncOpenIDMixin.create_logout_url(self, **kwargs)

    async def authorize_access_token(self, request) -> dict:
        return {"id_token": "id-token", "userinfo": {}}


class OAuthMock:
    def __init__(self, client: OAuthClientMock):
        self.client = client

    def create_client(self, name: str) -> OAuthClientMock:
        return self.client


class OpenIDProviderMock:
    """Signs in whoever the IdP vouched for, so the callback can be tested without a real user"""

    def __init__(self, session, claims: dict, use_default_groups: bool = False):
        pass

    def authenticate(self) -> tuple[str, timedelta]:
        return "access-token", timedelta(hours=1)


def setup_oidc(monkeypatch: MonkeyPatch, client: OAuthClientMock | None = None, signout_enabled: bool = True):
    monkeypatch.setattr(auth_routes, "oauth", OAuthMock(client or OAuthClientMock()))
    monkeypatch.setattr(auth_routes.settings, "OIDC_SIGNOUT_ENABLED", signout_enabled)


def log_out(api_client: TestClient, user: TestUser, id_token: str | None = "id-token"):
    headers = dict(user.token)
    if id_token:
        headers["Cookie"] = f"{ID_TOKEN_COOKIE}={id_token}"
    response = api_client.post(api_routes.auth_logout, headers=headers)
    assert response.status_code == 200
    return response


def test_logout_ends_the_idp_session(api_client: TestClient, unique_user: TestUser, monkeypatch: MonkeyPatch):
    setup_oidc(monkeypatch)

    response = log_out(api_client, unique_user)

    redirect_url = urlsplit(response.json()["redirect_url"])
    assert f"{redirect_url.scheme}://{redirect_url.netloc}{redirect_url.path}" == END_SESSION_ENDPOINT
    query = parse_qs(redirect_url.query)
    # authlib adds a random state, which Mealie doesn't use
    assert len(query.pop("state")) == 1
    assert query == {
        "id_token_hint": ["id-token"],
        "client_id": [OAuthClientMock.client_id],
        # the same page Mealie's own logout lands on
        "post_logout_redirect_uri": ["http://testserver/login?direct=1"],
    }

    # the ID token has done its job, so it goes with the session
    cookies = response.headers.get_list("set-cookie")
    assert any(c.startswith(f"{ID_TOKEN_COOKIE}=") and "Max-Age=0" in c for c in cookies)


def test_logout_returns_to_the_configured_url(api_client: TestClient, unique_user: TestUser, monkeypatch: MonkeyPatch):
    setup_oidc(monkeypatch)
    monkeypatch.setattr(auth_routes.settings, "OIDC_SIGNOUT_REDIRECT_URL", "https://mealie.example/login")

    response = log_out(api_client, unique_user)

    query = parse_qs(urlsplit(response.json()["redirect_url"]).query)
    assert query["post_logout_redirect_uri"] == ["https://mealie.example/login"]


@pytest.mark.parametrize(
    "client, signout_enabled, id_token",
    [
        (OAuthClientMock(), False, "id-token"),
        (OAuthClientMock(), True, None),
        (OAuthClientMock(metadata={}), True, "id-token"),
        (OAuthClientMock(metadata_error=httpx.ConnectError("the IdP is unreachable")), True, "id-token"),
        (OAuthClientMock(metadata_error=ValueError("the IdP's metadata isn't JSON")), True, "id-token"),
    ],
    ids=[
        "sign-out disabled",
        "not signed in through OIDC",
        "no end_session_endpoint",
        "IdP unreachable",
        "invalid metadata",
    ],
)
def test_logout_leaves_the_idp_alone(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: MonkeyPatch,
    client: OAuthClientMock,
    signout_enabled: bool,
    id_token: str | None,
):
    """Mealie's own logout has to work regardless; only the extra redirect is skipped."""
    setup_oidc(monkeypatch, client, signout_enabled)

    response = log_out(api_client, unique_user, id_token)

    assert response.json()["redirect_url"] is None


@pytest.mark.parametrize("signout_enabled", [True, False], ids=["enabled", "disabled"])
def test_oauth_callback_keeps_the_id_token_for_logout(
    api_client: TestClient, monkeypatch: MonkeyPatch, signout_enabled: bool
):
    setup_oidc(monkeypatch, signout_enabled=signout_enabled)
    monkeypatch.setattr(openid_provider, "OpenIDProvider", OpenIDProviderMock)

    response = api_client.get(api_routes.auth_oauth_callback)
    assert response.status_code == 200

    id_token_cookies = [c for c in response.headers.get_list("set-cookie") if c.startswith(f"{ID_TOKEN_COOKIE}=")]
    if signout_enabled:
        assert len(id_token_cookies) == 1
        # only Mealie's own auth routes need it, and never the page's scripts
        assert "HttpOnly" in id_token_cookies[0]
        assert "Path=/api/auth" in id_token_cookies[0]
    else:
        assert id_token_cookies == []


def test_refresh_renews_the_id_token_cookie(api_client: TestClient, unique_user: TestUser):
    """The ID token has to outlive every refreshed session, or a long session couldn't end the IdP's."""
    headers = {**unique_user.token, "Cookie": f"{ID_TOKEN_COOKIE}=id-token"}

    response = api_client.post(api_routes.auth_refresh, headers=headers)
    assert response.status_code == 200

    cookies = response.headers.get_list("set-cookie")
    assert any(c.startswith(f"{ID_TOKEN_COOKIE}=id-token") for c in cookies)
