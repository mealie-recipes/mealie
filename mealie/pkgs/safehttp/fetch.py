import asyncio
import random
import time
from dataclasses import dataclass

import httpx
from httpx import AsyncClient

from mealie.core.config import get_app_settings
from mealie.core.root_logger import get_logger
from mealie.core.settings.settings import ScraperProxyMode

from . import flaresolverr
from .transport import AsyncSafeTransport

SCRAPER_TIMEOUT = 15

# Overall wall-clock budget for a single fetch, across all impersonation attempts and backoffs.
# Bounds worst-case latency when a site repeatedly blocks or stalls us.
SCRAPER_TOTAL_TIMEOUT = 45

BROWSER_IMPERSONATIONS = [
    "chrome",
    "firefox",
    "safari",
    "edge",
]

NON_CHALLENGE_4XX = frozenset({404, 410})
RATE_LIMIT_STATUS_CODES = frozenset({429, 503})

# Substrings found in the bodies of bot-challenge/interstitial pages that are served with a
# 200 status (so status/header checks alone would treat them as a successful fetch). Kept
# specific to anti-bot infrastructure identifiers to avoid false positives on real content.
_CHALLENGE_BODY_MARKERS: tuple[bytes, ...] = (
    b"__cf_chl",
    b"cf-browser-verification",
    b"/cdn-cgi/challenge-platform",
    b"challenges.cloudflare.com",
    b"_incapsula_resource",
    b"distil_r_captcha",
    b"px-captcha",
    b"perimeterx",
    b"datadome",
)
_CHALLENGE_BODY_SAMPLE = 4096

_BASE_BACKOFF = 1.0
_MAX_BACKOFF = 5.0
_BACKOFF_JITTER = 0.5

logger = get_logger()


class ForceTimeoutException(Exception):
    """Raised when reading a response body exceeds the fetch timeout."""


@dataclass
class FetchResult:
    """The outcome of a resilient fetch, decoupled from the (now-closed) streaming response."""

    content: bytes
    status_code: int
    url: str
    headers: httpx.Headers
    encoding: str | None

    @property
    def text(self) -> str:
        # Mirrors the decoding behavior of requests' `text` property.
        try:
            return str(self.content, self.encoding, errors="replace")  # type: ignore[arg-type]
        except (LookupError, TypeError):
            # LookupError: unknown encoding name. TypeError: encoding is None.
            return str(self.content, errors="replace")


def is_challenge_status(status_code: int) -> bool:
    if status_code == 503:
        return True
    if 400 <= status_code < 500:
        return status_code not in NON_CHALLENGE_4XX
    return False


def headers_indicate_challenge(headers: httpx.Headers) -> bool:
    # Cloudflare sets `cf-mitigated: challenge` on interstitial/challenge responses,
    # which can otherwise carry a 200 status.
    return "cf-mitigated" in headers


def body_indicates_challenge(content: bytes) -> bool:
    sample = content[:_CHALLENGE_BODY_SAMPLE].lower()
    return any(marker in sample for marker in _CHALLENGE_BODY_MARKERS)


def _build_transport(impersonate: str, proxy: str | None = None) -> AsyncSafeTransport:
    kwargs: dict = {
        "impersonate": impersonate,
        "default_headers": True,
        # disable SSL verification since we can handle untrusted data and some sites don't have certs
        # (this also covers the proxy connection, so no separate proxy-verify knob is needed)
        "verify": False,
    }
    if proxy:
        kwargs["proxy"] = proxy
    return AsyncSafeTransport(**kwargs)


async def _read_capped(resp: httpx.Response, timeout: int) -> bytes:
    """
    Reads a streaming body, aborting if it takes longer than ``timeout`` seconds.

    Mitigates abuse from URLs that serve arbitrarily large or slow content.
    """
    content = b""
    start_time = time.monotonic()
    async for chunk in resp.aiter_bytes(chunk_size=1024):
        content += chunk
        if time.monotonic() - start_time > timeout:
            raise ForceTimeoutException()
    return content


async def _sleep_backoff(retry_after: str | None, deadline: float) -> None:
    """Sleeps a jittered backoff before the next attempt, never past the overall deadline."""
    delay = _BASE_BACKOFF
    if retry_after:
        try:
            # Retry-After may be a delta-seconds integer; if it's an HTTP-date we ignore it.
            delay = max(delay, float(retry_after))
        except ValueError:
            pass

    delay = min(delay, _MAX_BACKOFF) + random.uniform(0, _BACKOFF_JITTER)

    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return
    await asyncio.sleep(min(delay, remaining))


async def _attempt(
    url: str,
    method: str,
    timeout: int,
    impersonation: str,
    read_body: bool,
    proxy: str | None,
) -> tuple[FetchResult | None, bool, int, str | None]:
    """
    Performs a single fetch attempt with one browser impersonation.

    Returns ``(result, blocked, status_code, retry_after)``:
    - ``result`` is set on success (and ``blocked`` is False).
    - ``blocked`` is True when the response looks like a bot challenge and rotating to another
      fingerprint may help.
    - When both ``result`` is None and ``blocked`` is False, the response was a hard error that
      rotating won't fix, and the caller should stop.
    """
    transport = _build_transport(impersonation, proxy)
    async with AsyncClient(transport=transport) as client:
        async with client.stream(method, url, timeout=timeout, follow_redirects=True) as resp:
            status_code = resp.status_code
            retry_after = resp.headers.get("Retry-After")

            blocked = is_challenge_status(status_code) or headers_indicate_challenge(resp.headers)

            if blocked:
                logger.debug(f'Challenge/block detected (status={status_code}) with impersonation "{impersonation}"')
                return None, True, status_code, retry_after

            if status_code >= 400:
                # A genuine client/server error (e.g. 404, 410, 500) that a different fingerprint
                # won't resolve. Stop rotating.
                logger.debug(f'Error status code {status_code} with impersonation "{impersonation}"')
                return None, False, status_code, retry_after

            content = b""
            if read_body:
                content = await _read_capped(resp, timeout)
                if body_indicates_challenge(content):
                    logger.debug(f'Challenge page body detected with impersonation "{impersonation}"')
                    return None, True, status_code, retry_after

            result = FetchResult(
                content=content,
                status_code=status_code,
                url=str(resp.url),
                headers=resp.headers,
                encoding=resp.encoding,
            )
            return result, False, status_code, retry_after


async def _rotate(
    url: str,
    method: str,
    timeout: int,
    read_body: bool,
    proxy: str | None,
    deadline: float,
) -> tuple[FetchResult | None, bool]:
    """
    Cycles through browser impersonations (in randomized order) for a single egress path
    (direct or via ``proxy``).

    Returns ``(result, blocked)``. ``blocked`` is True only when every impersonation was rejected
    by a challenge/block -- i.e. the failure might be worth escalating (e.g. to a proxy). It is
    False on success or on a hard error, where escalation wouldn't help.
    """
    impersonations = list(BROWSER_IMPERSONATIONS)
    random.shuffle(impersonations)

    for index, impersonation in enumerate(impersonations):
        if time.monotonic() >= deadline:
            logger.debug("Scraper budget exhausted before trying all impersonations")
            break

        logger.debug(f'Trying browser impersonation: "{impersonation}"')
        result, blocked, status_code, retry_after = await _attempt(
            url, method, timeout, impersonation, read_body, proxy
        )

        if result is not None:
            return result, False

        if not blocked:
            # Hard error; rotating fingerprints won't help.
            return None, False

        is_last = index == len(impersonations) - 1
        if not is_last and status_code in RATE_LIMIT_STATUS_CODES:
            await _sleep_backoff(retry_after, deadline)

    return None, True


def _solution_to_result(solution: flaresolverr.FlareSolverrSolution) -> FetchResult:
    return FetchResult(
        content=solution.html.encode("utf-8", errors="replace"),
        status_code=solution.status_code,
        url=solution.url,
        headers=httpx.Headers({"content-type": "text/html; charset=utf-8"}),
        encoding="utf-8",
    )


async def resilient_fetch(
    url: str,
    *,
    method: str = "GET",
    timeout: int = SCRAPER_TIMEOUT,
    allow_flaresolverr: bool = True,
) -> FetchResult | None:
    """
    Fetches a URL while cycling through browser TLS impersonations (via httpx-curl-cffi) to
    bypass bot-detection systems that fingerprint the TLS handshake (JA3/JA4), such as Cloudflare.

    Impersonations are tried in a randomized order. On a detected challenge/block (a challenge
    status code, a ``cf-mitigated`` header, or challenge markers in an otherwise-200 body) the
    next fingerprint is tried, with a short jittered backoff for rate-limit statuses. A genuine
    error status (e.g. 404) stops the rotation immediately, since a new fingerprint won't help.

    When ``SCRAPER_PROXY_URL`` is configured, requests egress through it: in ``always`` mode every
    request uses the proxy; in ``fallback`` mode a direct attempt is made first and the proxy is
    only used to retry when every direct impersonation was blocked.

    As a last resort, if the fetch is still blocked and ``SCRAPER_FLARESOLVERR_URL`` is configured,
    the request is escalated to FlareSolverr (a headless browser). This only applies to HTML fetches
    (``allow_flaresolverr`` and a body-returning method), since FlareSolverr returns HTML, not the
    binary content an image download needs.

    The whole operation is bounded by ``SCRAPER_TOTAL_TIMEOUT``, and each attempt's body read is
    bounded by ``timeout`` seconds, to mitigate abuse from URLs that serve arbitrarily large content.

    Returns a ``FetchResult`` for the first successful response, or ``None`` if every impersonation
    was blocked, the server returned a hard error, or the budget was exhausted.
    """
    logger.debug(f"Fetching URL: {url}")

    read_body = method.upper() != "HEAD"
    deadline = time.monotonic() + SCRAPER_TOTAL_TIMEOUT

    settings = get_app_settings()
    proxy = settings.SCRAPER_PROXY_URL or None
    proxy_first = bool(proxy) and settings.SCRAPER_PROXY_MODE == ScraperProxyMode.always

    result, blocked = await _rotate(url, method, timeout, read_body, proxy if proxy_first else None, deadline)
    if result is not None:
        return result

    # In `fallback` mode, escalate to the proxy only when a direct attempt was blocked (not on a
    # hard error, and not if we already used the proxy above).
    if blocked and proxy and not proxy_first:
        logger.debug("Direct fetch blocked; retrying through configured proxy")
        result, blocked = await _rotate(url, method, timeout, read_body, proxy, deadline)
        if result is not None:
            return result

    # Final escalation: a real browser via FlareSolverr. HTML-only, and only when still blocked.
    # Note: the impersonation rotation above always runs first, so its SSRF guard (which rejects
    # private target IPs) has already vetted `url` before we hand it to FlareSolverr.
    if blocked and read_body and allow_flaresolverr and settings.SCRAPER_FLARESOLVERR_URL:
        logger.debug("Fetch still blocked; escalating to FlareSolverr")
        solution = await flaresolverr.solve(
            settings.SCRAPER_FLARESOLVERR_URL, url, settings.SCRAPER_FLARESOLVERR_TIMEOUT
        )
        if solution is not None:
            return _solution_to_result(solution)

    return result
