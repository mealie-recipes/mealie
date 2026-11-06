from unittest.mock import MagicMock

import httpx
import pytest

import mealie.services.scraper.recipe_scraper as recipe_scraper_module
from mealie.lang.providers import get_locale_provider
from mealie.pkgs.safehttp.fetch import FetchResult
from mealie.schema.recipe.recipe import Recipe
from mealie.services.scraper.recipe_scraper import RecipeScraper
from mealie.services.scraper.scraped_extras import ScrapedExtras
from mealie.services.scraper.scraper_strategies import ABCScraperStrategy

URL = "https://example.com/recipe"
BOT_WALL_HTML = "<html><body>Checking your browser...</body></html>"
RECIPE_HTML = "<html><body>RECIPE</body></html>"


def _fetch(html: str, *, via_flaresolverr: bool = False) -> FetchResult:
    return FetchResult(html.encode(), 200, URL, httpx.Headers(), "utf-8", via_flaresolverr)


class MarkerStrategy(ABCScraperStrategy):
    """Parses a recipe only from pages containing the RECIPE marker."""

    pages: list[str] = []

    def can_scrape(self) -> bool:
        return True

    async def get_html(self, url: str) -> str:
        return self.raw_html or ""

    async def parse(self, on_progress=None):
        MarkerStrategy.pages.append(self.raw_html or "")
        if self.raw_html and "RECIPE" in self.raw_html:
            return Recipe(name="Soup", slug="soup"), ScrapedExtras()
        return None, None


@pytest.fixture(autouse=True)
def _reset_pages():
    MarkerStrategy.pages = []
    yield
    MarkerStrategy.pages = []


def _patch_fetch(monkeypatch: pytest.MonkeyPatch, fetched: FetchResult, solved: FetchResult | None) -> list[str]:
    calls: list[str] = []

    async def mock_resilient_fetch(url: str) -> FetchResult:
        return fetched

    async def mock_fetch_via_flaresolverr(url: str) -> FetchResult | None:
        calls.append(url)
        return solved

    monkeypatch.setattr(recipe_scraper_module, "resilient_fetch", mock_resilient_fetch)
    monkeypatch.setattr(recipe_scraper_module, "fetch_via_flaresolverr", mock_fetch_via_flaresolverr)
    return calls


@pytest.mark.asyncio
async def test_escalates_to_flaresolverr_when_direct_html_yields_no_recipe(monkeypatch: pytest.MonkeyPatch):
    calls = _patch_fetch(monkeypatch, _fetch(BOT_WALL_HTML), _fetch(RECIPE_HTML, via_flaresolverr=True))

    scraper = RecipeScraper(MagicMock(), get_locale_provider(), scrapers=[MarkerStrategy])
    recipe, _ = await scraper.scrape(URL)

    assert recipe is not None
    assert MarkerStrategy.pages == [BOT_WALL_HTML, RECIPE_HTML]
    assert calls == [URL]


@pytest.mark.asyncio
async def test_no_recipe_and_no_flaresolverr_returns_none(monkeypatch: pytest.MonkeyPatch):
    calls = _patch_fetch(monkeypatch, _fetch(BOT_WALL_HTML), None)

    scraper = RecipeScraper(MagicMock(), get_locale_provider(), scrapers=[MarkerStrategy])
    recipe, _ = await scraper.scrape(URL)

    assert recipe is None
    assert MarkerStrategy.pages == [BOT_WALL_HTML]
    assert calls == [URL]


@pytest.mark.asyncio
async def test_no_second_escalation_when_fetch_already_used_flaresolverr(monkeypatch: pytest.MonkeyPatch):
    solved = _fetch(RECIPE_HTML, via_flaresolverr=True)
    calls = _patch_fetch(monkeypatch, _fetch(BOT_WALL_HTML, via_flaresolverr=True), solved)

    scraper = RecipeScraper(MagicMock(), get_locale_provider(), scrapers=[MarkerStrategy])
    recipe, _ = await scraper.scrape(URL)

    assert recipe is None
    assert MarkerStrategy.pages == [BOT_WALL_HTML]
    assert calls == []
