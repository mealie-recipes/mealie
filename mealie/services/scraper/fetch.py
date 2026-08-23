from mealie.pkgs import safehttp

SCRAPER_TIMEOUT = safehttp.SCRAPER_TIMEOUT
BROWSER_IMPERSONATIONS = safehttp.BROWSER_IMPERSONATIONS
ForceTimeoutException = safehttp.ForceTimeoutException


async def safe_scrape_html(url: str) -> str:
    """
    Scrapes the html from a url but will cancel the request
    if the request takes longer than SCRAPER_TIMEOUT seconds. This is used to mitigate
    DDOS attacks from users providing a url with arbitrary large content.

    Cycles through browser TLS impersonations (via httpx-curl-cffi) to bypass
    bot-detection systems that fingerprint the TLS handshake (JA3/JA4),
    such as Cloudflare.
    """
    result = await safehttp.resilient_fetch(url)
    return result.text if result else ""
