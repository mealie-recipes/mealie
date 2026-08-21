import httpx
import pytest

from mealie.pkgs.safehttp.transport import AsyncSafeTransport, InvalidDomainError

PRIVATE_TARGETS = [
    "http://127.0.0.1/x",
    "http://10.0.0.5/x",
    "http://192.168.1.10:8080/x",
    "http://169.254.169.254/latest/meta-data/",  # cloud metadata endpoint
]


def _transport(**kwargs) -> AsyncSafeTransport:
    return AsyncSafeTransport(impersonate="chrome", default_headers=True, verify=False, **kwargs)


@pytest.mark.parametrize("url", PRIVATE_TARGETS)
@pytest.mark.asyncio
async def test_rejects_private_targets_by_default(url: str, monkeypatch):
    """The SSRF guard stays on unless a caller explicitly opts out."""
    monkeypatch.setattr(
        AsyncSafeTransport.__bases__[0],
        "handle_async_request",
        _unreachable,
    )

    with pytest.raises(InvalidDomainError):
        await _transport().handle_async_request(httpx.Request("GET", url))


@pytest.mark.parametrize("url", PRIVATE_TARGETS)
@pytest.mark.asyncio
async def test_allow_private_reaches_the_underlying_transport(url: str, monkeypatch):
    """With the opt-out set, the request is handed straight to the real transport."""
    monkeypatch.setattr(
        AsyncSafeTransport.__bases__[0],
        "handle_async_request",
        _sentinel_response,
    )

    response = await _transport(allow_private=True).handle_async_request(httpx.Request("GET", url))

    assert response.status_code == 204


async def _unreachable(self, request: httpx.Request) -> httpx.Response:
    raise AssertionError(f"guard should have rejected {request.url} before reaching the transport")


async def _sentinel_response(self, request: httpx.Request) -> httpx.Response:
    return httpx.Response(204, request=request)
