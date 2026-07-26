import time
from dataclasses import dataclass

import httpx
from httpx import AsyncClient

from mealie.core.root_logger import get_logger

from .transport import AsyncSafeTransport

SCRAPER_TIMEOUT = 15

BROWSER_IMPERSONATIONS = [
    "chrome",
    "firefox",
    "safari",
    "edge",
]

logger = get_logger()


class ForceTimeoutException(Exception):
    """Raised when reading a response body exceeds SCRAPER_TIMEOUT seconds."""


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


def _build_transport(impersonate: str) -> AsyncSafeTransport:
    return AsyncSafeTransport(
        impersonate=impersonate,
        default_headers=True,
        # disable SSL verification since we can handle untrusted data and some sites don't have certs
        verify=False,
    )


async def resilient_fetch(
    url: str,
    *,
    method: str = "GET",
    timeout: int = SCRAPER_TIMEOUT,
) -> FetchResult | None:
    """
    Fetches a URL while cycling through browser TLS impersonations (via httpx-curl-cffi) to
    bypass bot-detection systems that fingerprint the TLS handshake (JA3/JA4), such as Cloudflare.

    The request is cancelled if reading the body takes longer than ``timeout`` seconds, to
    mitigate abuse from URLs that serve arbitrarily large content.

    Returns a ``FetchResult`` for the first non-forbidden response, or ``None`` if every
    impersonation was rejected (403) or the server returned another error status.
    """
    logger.debug(f"Fetching URL: {url}")

    read_body = method.upper() != "HEAD"

    for impersonation in BROWSER_IMPERSONATIONS:
        logger.debug(f'Trying browser impersonation: "{impersonation}"')

        transport = _build_transport(impersonation)
        async with AsyncClient(transport=transport) as client:
            async with client.stream(
                method,
                url,
                timeout=timeout,
                follow_redirects=True,
            ) as resp:
                if resp.status_code == 403:
                    logger.debug(f'403 Forbidden with impersonation "{impersonation}", trying next')
                    continue

                if resp.status_code >= 400:
                    logger.debug(f'Error status code {resp.status_code} with impersonation "{impersonation}"')
                    return None

                content = b""
                if read_body:
                    start_time = time.time()
                    async for chunk in resp.aiter_bytes(chunk_size=1024):
                        content += chunk

                        if time.time() - start_time > timeout:
                            raise ForceTimeoutException()

                return FetchResult(
                    content=content,
                    status_code=resp.status_code,
                    url=str(resp.url),
                    headers=resp.headers,
                    encoding=resp.encoding,
                )

    return None
