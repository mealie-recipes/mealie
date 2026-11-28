"""Client metadata validation for public MCP OAuth clients."""

import socket

import httpx
import pytest
from mcp.shared.auth import InvalidRedirectUriError
from pydantic import AnyUrl

from mealie.mcp import oauth

CLIENT_ID = "https://chatgpt.com/oauth/client.json"
REDIRECT = "https://chatgpt.com/connector_platform_oauth_redirect"


@pytest.mark.asyncio
async def test_cimd_selects_public_method_from_supported_methods(monkeypatch):
    seen = []
    payload = {
        "client_id": CLIENT_ID,
        "client_name": "ChatGPT",
        "redirect_uris": [REDIRECT],
        "token_endpoint_auth_method": "private_key_jwt",
        "token_endpoint_auth_methods_supported": ["none", "private_key_jwt"],
    }

    def respond(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=payload)

    real_client = httpx.AsyncClient

    def client_factory(**kwargs):
        return real_client(transport=httpx.MockTransport(respond), **kwargs)

    monkeypatch.setattr(
        oauth.socket, "getaddrinfo", lambda *_args, **_kwargs: [(socket.AF_INET, 0, 0, "", ("93.184.215.14", 443))]
    )
    monkeypatch.setattr(oauth.httpx, "AsyncClient", client_factory)
    client = await oauth._fetch_client_metadata(CLIENT_ID)
    assert client is not None
    assert client.token_endpoint_auth_method == "none"
    assert str(client.redirect_uris[0]) == REDIRECT
    assert seen[0].url.host == "93.184.215.14"
    assert seen[0].headers["host"] == "chatgpt.com"
    assert seen[0].extensions["sni_hostname"] == "chatgpt.com"

    payload["token_endpoint_auth_methods_supported"] = ["private_key_jwt"]
    assert await oauth._fetch_client_metadata(CLIENT_ID) is None


@pytest.mark.asyncio
async def test_cimd_rejects_private_dns_addresses(monkeypatch):
    monkeypatch.setattr(
        oauth.socket, "getaddrinfo", lambda *_args, **_kwargs: [(socket.AF_INET, 0, 0, "", ("127.0.0.1", 443))]
    )
    assert await oauth._fetch_client_metadata(CLIENT_ID) is None


CODEX_ID = "https://chatgpt.com/oauth/codex/client.json"


def _codex_client() -> oauth.McpClientInformation:
    return oauth.McpClientInformation.model_validate(
        {
            "client_id": CODEX_ID,
            "application_type": "native",
            "redirect_uris": ["http://127.0.0.1/callback", "http://localhost/callback"],
            "token_endpoint_auth_method": "none",
        }
    )


@pytest.mark.parametrize(
    "redirect",
    ["http://127.0.0.1:58724/callback", "http://localhost:4000/callback", "http://127.0.0.1/callback"],
)
def test_loopback_redirect_accepts_any_port(redirect):
    client = _codex_client()
    assert str(client.validate_redirect_uri(AnyUrl(redirect))) == redirect


@pytest.mark.parametrize(
    "redirect",
    [
        "http://127.0.0.1:58724/other",
        "http://192.168.1.10:58724/callback",
        "https://127.0.0.1:58724/callback",
        "http://127.0.0.1:58724/callback?next=x",
        "http://evil.example:58724/callback",
    ],
)
def test_loopback_redirect_still_requires_registered_host_and_path(redirect):
    with pytest.raises(InvalidRedirectUriError):
        _codex_client().validate_redirect_uri(AnyUrl(redirect))


def test_https_redirect_still_requires_exact_match():
    client = oauth.McpClientInformation.model_validate(
        {"client_id": CLIENT_ID, "redirect_uris": [REDIRECT], "token_endpoint_auth_method": "none"}
    )
    assert str(client.validate_redirect_uri(AnyUrl(REDIRECT))) == REDIRECT
    with pytest.raises(InvalidRedirectUriError):
        client.validate_redirect_uri(AnyUrl("https://chatgpt.com:8443/connector_platform_oauth_redirect"))


def _serve_metadata(monkeypatch, payload: dict) -> list[httpx.Request]:
    seen: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=payload)

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        oauth.socket, "getaddrinfo", lambda *_args, **_kwargs: [(socket.AF_INET, 0, 0, "", ("93.184.215.14", 443))]
    )
    monkeypatch.setattr(
        oauth.httpx, "AsyncClient", lambda **kwargs: real_client(transport=httpx.MockTransport(respond), **kwargs)
    )
    return seen


@pytest.mark.asyncio
async def test_cimd_without_application_type_allows_loopback(monkeypatch):
    # Shape of the MCP specification's own client metadata document example
    _serve_metadata(
        monkeypatch,
        {"client_id": CODEX_ID, "client_name": "Example", "redirect_uris": ["http://127.0.0.1:3000/callback"]},
    )
    client = await oauth._fetch_client_metadata(CODEX_ID)
    assert client is not None
    assert client.application_type == "native"


@pytest.mark.asyncio
async def test_cimd_metadata_is_cached_and_drops_unknown_scopes(monkeypatch):
    oauth._client_metadata_cache.clear()
    seen = _serve_metadata(
        monkeypatch,
        {
            "client_id": CODEX_ID,
            "application_type": "native",
            "redirect_uris": ["http://127.0.0.1/callback"],
            "scope": "openid offline_access recipes:read",
        },
    )
    first = await oauth._cached_client_metadata(CODEX_ID)
    second = await oauth._cached_client_metadata(CODEX_ID)
    assert first is not None and second is first
    assert first.scope == "recipes:read"
    assert len(seen) == 1
    oauth._client_metadata_cache.clear()
