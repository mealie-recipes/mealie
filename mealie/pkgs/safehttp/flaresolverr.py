from dataclasses import dataclass, field

import httpx

from mealie.core.root_logger import get_logger

logger = get_logger()

# Extra seconds allowed for the HTTP round-trip on top of FlareSolverr's own solve budget,
# to account for browser startup and network overhead.
_HTTP_OVERHEAD_SECONDS = 15


@dataclass
class FlareSolverrSolution:
    """The useful parts of a successful FlareSolverr solve."""

    html: str
    status_code: int
    url: str
    cookies: list[dict] = field(default_factory=list)
    user_agent: str = ""


async def solve(base_url: str, url: str, timeout: int) -> FlareSolverrSolution | None:
    """
    Asks a FlareSolverr instance to fetch ``url`` with a real (headless) browser, solving any
    JS/Cloudflare challenge along the way.

    FlareSolverr is a REST service, not a proxy: we POST a job to ``{base_url}/v1`` and read the
    rendered HTML back out of the response envelope.

    Returns ``None`` (never raises) on any failure -- an unreachable or misbehaving FlareSolverr
    must only fail this escalation, never break scraping.
    """
    endpoint = base_url.rstrip("/") + "/v1"
    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": timeout * 1000,  # FlareSolverr expects milliseconds
    }

    try:
        async with httpx.AsyncClient(timeout=timeout + _HTTP_OVERHEAD_SECONDS) as client:
            resp = await client.post(endpoint, json=payload)
    except Exception:
        logger.exception(f"FlareSolverr request failed for {url}")
        return None

    if resp.status_code != 200:
        logger.warning(f"FlareSolverr returned HTTP {resp.status_code} for {url}")
        return None

    try:
        data = resp.json()
    except Exception:
        logger.exception(f"FlareSolverr returned a non-JSON response for {url}")
        return None

    if data.get("status") != "ok":
        logger.warning(f"FlareSolverr could not solve {url}: {data.get('message')}")
        return None

    solution = data.get("solution") or {}
    html = solution.get("response")
    if not html:
        logger.warning(f"FlareSolverr returned an empty solution for {url}")
        return None

    return FlareSolverrSolution(
        html=html,
        status_code=solution.get("status", 200),
        url=solution.get("url", url),
        cookies=solution.get("cookies", []),
        user_agent=solution.get("userAgent", ""),
    )
