import httpx
import pytest

from mealie.pkgs.safehttp import flaresolverr


class _FakeHTTPResponse:
    def __init__(self, status_code: int, json_data=None, raise_json: bool = False):
        self.status_code = status_code
        self._json_data = json_data
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            raise ValueError("not json")
        return self._json_data


class _FakePostClient:
    """Stands in for httpx.AsyncClient, capturing the POST and returning a scripted response."""

    last_call: dict = {}

    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, endpoint: str, json: dict):
        _FakePostClient.last_call = {"endpoint": endpoint, "json": json}
        if self._exc:
            raise self._exc
        return self._response


def _patch_client(monkeypatch, *, response=None, exc=None):
    monkeypatch.setattr(flaresolverr.httpx, "AsyncClient", lambda *a, **k: _FakePostClient(response=response, exc=exc))


_OK_ENVELOPE = {
    "status": "ok",
    "solution": {
        "url": "https://x/final",
        "status": 200,
        "response": "<html>solved</html>",
        "cookies": [{"name": "cf_clearance", "value": "abc"}],
        "userAgent": "Mozilla/5.0 ...",
    },
}


@pytest.mark.asyncio
async def test_solve_success_parses_solution(monkeypatch):
    _patch_client(monkeypatch, response=_FakeHTTPResponse(200, _OK_ENVELOPE))

    solution = await flaresolverr.solve("http://flaresolverr:8191", "https://x/r", 45)

    assert solution is not None
    assert solution.html == "<html>solved</html>"
    assert solution.status_code == 200
    assert solution.url == "https://x/final"
    assert solution.cookies == [{"name": "cf_clearance", "value": "abc"}]
    assert solution.user_agent == "Mozilla/5.0 ..."


@pytest.mark.asyncio
async def test_solve_builds_correct_request(monkeypatch):
    _patch_client(monkeypatch, response=_FakeHTTPResponse(200, _OK_ENVELOPE))

    # trailing slash on base URL should be normalized
    await flaresolverr.solve("http://flaresolverr:8191/", "https://x/r", 30)

    call = _FakePostClient.last_call
    assert call["endpoint"] == "http://flaresolverr:8191/v1"
    assert call["json"]["cmd"] == "request.get"
    assert call["json"]["url"] == "https://x/r"
    assert call["json"]["maxTimeout"] == 30_000  # seconds -> milliseconds


@pytest.mark.asyncio
async def test_solve_returns_none_on_http_error(monkeypatch):
    _patch_client(monkeypatch, response=_FakeHTTPResponse(500, {}))
    assert await flaresolverr.solve("http://fs:8191", "https://x/r", 30) is None


@pytest.mark.asyncio
async def test_solve_returns_none_on_error_status(monkeypatch):
    _patch_client(monkeypatch, response=_FakeHTTPResponse(200, {"status": "error", "message": "challenge failed"}))
    assert await flaresolverr.solve("http://fs:8191", "https://x/r", 30) is None


@pytest.mark.asyncio
async def test_solve_returns_none_on_empty_solution(monkeypatch):
    _patch_client(monkeypatch, response=_FakeHTTPResponse(200, {"status": "ok", "solution": {"response": ""}}))
    assert await flaresolverr.solve("http://fs:8191", "https://x/r", 30) is None


@pytest.mark.asyncio
async def test_solve_returns_none_on_non_json(monkeypatch):
    _patch_client(monkeypatch, response=_FakeHTTPResponse(200, raise_json=True))
    assert await flaresolverr.solve("http://fs:8191", "https://x/r", 30) is None


@pytest.mark.asyncio
async def test_solve_returns_none_on_connection_error(monkeypatch):
    _patch_client(monkeypatch, exc=httpx.ConnectError("unreachable"))
    assert await flaresolverr.solve("http://fs:8191", "https://x/r", 30) is None
