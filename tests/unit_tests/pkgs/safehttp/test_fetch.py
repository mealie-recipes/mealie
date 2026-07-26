from collections.abc import AsyncIterator

import httpx
import pytest

from mealie.pkgs.safehttp import fetch


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (200, False),
        (301, False),
        (400, True),
        (401, True),
        (402, True),
        (403, True),
        (406, True),
        (429, True),
        (451, True),
        (404, False),  # resource genuinely missing -> not worth rotating
        (410, False),
        (500, False),  # server error a new fingerprint won't fix
        (502, False),
        (503, True),  # WAFs use 503 during interstitials
        (504, False),
    ],
)
def test_is_challenge_status(status_code: int, expected: bool):
    assert fetch.is_challenge_status(status_code) is expected


def test_headers_indicate_challenge():
    assert fetch.headers_indicate_challenge(httpx.Headers({"cf-mitigated": "challenge"})) is True
    # header lookup is case-insensitive
    assert fetch.headers_indicate_challenge(httpx.Headers({"CF-Mitigated": "challenge"})) is True
    assert fetch.headers_indicate_challenge(httpx.Headers({"server": "cloudflare"})) is False
    assert fetch.headers_indicate_challenge(httpx.Headers({})) is False


def test_body_indicates_challenge():
    assert fetch.body_indicates_challenge(b"<html>...cf-browser-verification...</html>") is True
    # marker matching is case-insensitive
    assert fetch.body_indicates_challenge(b"<script src='/cdn-cgi/challenge-platform/x'></script>") is True
    assert fetch.body_indicates_challenge(b"<html><body>A normal recipe for cookies</body></html>") is False


def test_body_indicates_challenge_only_samples_head():
    # A marker past the sampled window should not be detected.
    body = b"x" * (fetch._CHALLENGE_BODY_SAMPLE + 100) + b"datadome"
    assert fetch.body_indicates_challenge(body) is False


# ---------------------------------------------------------------------------
# FetchResult.text
# ---------------------------------------------------------------------------
def test_fetch_result_text_decoding():
    assert fetch.FetchResult(b"h\xc3\xa9llo", 200, "http://x", httpx.Headers(), "utf-8").text == "héllo"
    # None encoding falls back to a blind decode
    assert fetch.FetchResult(b"abc", 200, "http://x", httpx.Headers(), None).text == "abc"
    # An unknown encoding name also falls back rather than raising
    assert fetch.FetchResult(b"abc", 200, "http://x", httpx.Headers(), "not-real").text == "abc"


# ---------------------------------------------------------------------------
# Fakes for the fetch loop
# ---------------------------------------------------------------------------
class _FakeResponse:
    def __init__(self, status_code: int, *, headers: dict | None = None, body: bytes = b"", url: str = "https://x/r"):
        self.status_code = status_code
        self.headers = httpx.Headers(headers or {})
        self.encoding = "utf-8"
        self.url = url
        self._body = body

    async def aiter_bytes(self, chunk_size: int = 1024) -> AsyncIterator[bytes]:
        for i in range(0, len(self._body), chunk_size):
            yield self._body[i : i + chunk_size]

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeClient:
    def __init__(self, response: _FakeResponse):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def stream(self, method: str, url: str, **kwargs):
        return self._response


def _patch_responses(monkeypatch, responses: list[_FakeResponse]) -> dict:
    """Scripts consecutive attempts to return the given responses, and counts attempts made."""
    state = {"queue": list(responses), "attempts": 0}

    def make_client(*args, **kwargs):
        state["attempts"] += 1
        return _FakeClient(state["queue"].pop(0))

    monkeypatch.setattr(fetch, "AsyncClient", make_client)
    monkeypatch.setattr(fetch, "_build_transport", lambda impersonate: None)
    return state


# ---------------------------------------------------------------------------
# resilient_fetch loop
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_success_on_first_attempt(monkeypatch):
    state = _patch_responses(monkeypatch, [_FakeResponse(200, body=b"<html>recipe</html>")])
    result = await fetch.resilient_fetch("https://x/r")

    assert result is not None
    assert result.status_code == 200
    assert result.content == b"<html>recipe</html>"
    assert state["attempts"] == 1


@pytest.mark.asyncio
async def test_rotates_through_all_impersonations_on_block(monkeypatch):
    state = _patch_responses(monkeypatch, [_FakeResponse(403) for _ in fetch.BROWSER_IMPERSONATIONS])
    result = await fetch.resilient_fetch("https://x/r")

    assert result is None
    assert state["attempts"] == len(fetch.BROWSER_IMPERSONATIONS)


@pytest.mark.asyncio
async def test_rotates_past_200_challenge_body(monkeypatch):
    state = _patch_responses(
        monkeypatch,
        [
            _FakeResponse(200, body=b"<html>__cf_chl just a moment</html>"),
            _FakeResponse(200, body=b"<html>real recipe</html>"),
        ],
    )
    result = await fetch.resilient_fetch("https://x/r")

    assert result is not None
    assert result.content == b"<html>real recipe</html>"
    assert state["attempts"] == 2


@pytest.mark.asyncio
async def test_hard_error_stops_immediately(monkeypatch):
    state = _patch_responses(monkeypatch, [_FakeResponse(404) for _ in fetch.BROWSER_IMPERSONATIONS])
    result = await fetch.resilient_fetch("https://x/r")

    assert result is None
    assert state["attempts"] == 1  # did not rotate on a 404


@pytest.mark.asyncio
async def test_head_request_skips_body(monkeypatch):
    # A body that *would* look like a challenge is ignored for HEAD (no body is read).
    state = _patch_responses(monkeypatch, [_FakeResponse(200, body=b"__cf_chl")])
    result = await fetch.resilient_fetch("https://x/r", method="HEAD")

    assert result is not None
    assert result.content == b""
    assert state["attempts"] == 1


@pytest.mark.asyncio
async def test_rate_limit_triggers_backoff_then_succeeds(monkeypatch):
    slept: list[float] = []

    async def fake_sleep(delay: float):
        slept.append(delay)

    monkeypatch.setattr(fetch.asyncio, "sleep", fake_sleep)
    state = _patch_responses(
        monkeypatch,
        [_FakeResponse(429, headers={"Retry-After": "2"}), _FakeResponse(200, body=b"ok")],
    )

    result = await fetch.resilient_fetch("https://x/r")

    assert result is not None
    assert result.content == b"ok"
    assert state["attempts"] == 2
    assert len(slept) == 1
    assert slept[0] >= 2.0  # honored Retry-After


@pytest.mark.asyncio
async def test_no_backoff_on_plain_403(monkeypatch):
    slept: list[float] = []

    async def fake_sleep(delay: float):
        slept.append(delay)

    monkeypatch.setattr(fetch.asyncio, "sleep", fake_sleep)
    _patch_responses(monkeypatch, [_FakeResponse(403), _FakeResponse(200, body=b"ok")])

    result = await fetch.resilient_fetch("https://x/r")

    assert result is not None
    assert slept == []  # 403 rotates immediately, no rate-limit backoff
