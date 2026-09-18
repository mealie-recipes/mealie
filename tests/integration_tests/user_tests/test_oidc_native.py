from authlib.integrations.starlette_client import OAuthError
from fastapi.testclient import TestClient
from joserfc.errors import InvalidClaimError
from pytest import MonkeyPatch

from mealie.app import app
from mealie.routes.auth import auth as auth_routes
from tests.utils import api_routes

native_token_request = {
    "code": "expired-authorization-code",
    "code_verifier": "code-verifier",
    "redirect_uri": "mealie://oidc-callback",
    "nonce": "nonce",
}


class OAuthClientMock:
    """Stands in for the authlib OIDC client, failing the way a rejected code or id_token does"""

    def __init__(self, token_error: Exception | None = None, id_token_error: Exception | None = None):
        self.token_error = token_error
        self.id_token_error = id_token_error

    async def fetch_access_token(self, **kwargs) -> dict:
        if self.token_error:
            raise self.token_error
        return {"access_token": "access-token", "id_token": "id-token"}

    async def parse_id_token(self, token, nonce=None) -> dict:
        if self.id_token_error:
            raise self.id_token_error
        return {}


class OAuthMock:
    def __init__(self, client: OAuthClientMock):
        self.client = client

    def create_client(self, name: str) -> OAuthClientMock:
        return self.client


def setup_oidc(
    monkeypatch: MonkeyPatch, token_error: Exception | None = None, id_token_error: Exception | None = None
) -> None:
    monkeypatch.setattr(type(auth_routes.settings), "OIDC_READY", property(lambda self: True))
    client = OAuthClientMock(token_error=token_error, id_token_error=id_token_error)
    monkeypatch.setattr(auth_routes, "oauth", OAuthMock(client), raising=False)


def test_native_config_returns_404_when_oidc_not_configured(api_client: TestClient):
    response = api_client.get(api_routes.auth_oauth_native_config)

    assert response.status_code == 404
    assert response.json()["detail"] == "OIDC is not configured"


def test_native_token_returns_404_when_oidc_not_configured(api_client: TestClient):
    response = api_client.post(api_routes.auth_oauth_native_token, json=native_token_request)

    assert response.status_code == 404
    assert response.json()["detail"] == "OIDC is not configured"


def test_native_token_returns_401_when_code_is_rejected(api_client: TestClient, monkeypatch: MonkeyPatch):
    setup_oidc(monkeypatch, token_error=OAuthError("invalid_grant", "authorization code is invalid or expired"))

    response = api_client.post(api_routes.auth_oauth_native_token, json=native_token_request)

    assert response.status_code == 401


def test_native_token_returns_500_on_unexpected_errors(monkeypatch: MonkeyPatch):
    setup_oidc(monkeypatch, token_error=RuntimeError("the IdP is unreachable"))

    # anything that isn't an OAuthError is a server-side failure, not a bad code, so it must not
    # become a 401; this client returns the 500 instead of re-raising the way the shared one does
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(api_routes.auth_oauth_native_token, json=native_token_request)

    assert response.status_code == 500


def test_native_token_returns_500_when_id_token_is_rejected(monkeypatch: MonkeyPatch):
    setup_oidc(monkeypatch, id_token_error=InvalidClaimError("nonce"))

    # authlib validates the id_token with joserfc, whose errors are not OAuthError, so a bad nonce
    # or signature is a 500 here, matching the web /oauth/callback route's unwrapped behavior
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(api_routes.auth_oauth_native_token, json=native_token_request)

    assert response.status_code == 500
