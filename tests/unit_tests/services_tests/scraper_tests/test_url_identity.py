from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest

import mealie.services.scraper.recipe_scraper as recipe_scraper_module
from mealie.lang.providers import get_locale_provider
from mealie.pkgs.safehttp.fetch import FetchResult
from mealie.schema.openai.recipe import OpenAIRecipe, OpenAIRecipeIngredient, OpenAIRecipeInstruction
from mealie.services.openai import OpenAIService, transcription
from mealie.services.scraper.recipe_scraper import RecipeScraper
from mealie.services.scraper.scraper_strategies import (
    ABCScraperStrategy,
    RecipeScraperOpenAI,
    RecipeScraperOpenAITranscription,
    RecipeScraperOpenGraph,
)

SHARE_URL = "https://www.facebook.com/share/r/1DWziuVHRi/"
REEL_URL = "https://www.facebook.com/reel/1433866715330175/"


def _html_fetch(url: str, html: str = "<html></html>") -> FetchResult:
    return FetchResult(html.encode(), 200, url, httpx.Headers(), "utf-8")


def test_resource_url_prefers_landing_url():
    strategy = RecipeScraperOpenGraph(
        SHARE_URL,
        get_locale_provider(),
        repos=None,  # type: ignore[arg-type]
        resolved_url=REEL_URL,
    )

    assert strategy.resource_url == REEL_URL
    assert strategy.url == SHARE_URL


def test_resource_url_falls_back_to_supplied_url():
    strategy = RecipeScraperOpenGraph(
        SHARE_URL,
        get_locale_provider(),
        repos=None,  # type: ignore[arg-type]
    )

    assert strategy.resource_url == SHARE_URL


def test_transcription_classifies_the_landing_url(monkeypatch: pytest.MonkeyPatch):
    classified: list[str] = []
    monkeypatch.setattr(transcription, "is_video_url", lambda url: classified.append(url) or True)

    repos = MagicMock()
    repos.group_ai_provider_settings.get_one.return_value = MagicMock(audio_provider_enabled=True)

    strategy = RecipeScraperOpenAITranscription(
        SHARE_URL,
        get_locale_provider(),
        repos,
        resolved_url=REEL_URL,
    )

    assert strategy.can_scrape() is True
    assert classified == [REEL_URL]


def test_openai_strategy_passes_resolved_url_into_workflow():
    strategy = RecipeScraperOpenAI(
        SHARE_URL,
        get_locale_provider(),
        MagicMock(),
        raw_html="<html></html>",
        resolved_url=REEL_URL,
    )

    ctx = strategy.build_context()

    assert ctx.input.url == SHARE_URL
    assert ctx.resolved_url == REEL_URL


@pytest.mark.asyncio
async def test_transcription_downloads_landing_url_and_keeps_org_url(monkeypatch: pytest.MonkeyPatch):
    downloaded: list[str] = []

    def mock_download_video(url: str, temp_path: Path):
        downloaded.append(url)
        return {
            "audio": temp_path / "mealie.mp3",
            "subtitle": None,
            "title": "A reel",
            "description": "desc",
            "thumbnail_url": None,
            "transcription": "mix flour and water",
        }

    async def mock_resolve_transcription(video_data, openai_service, before_transcribe=None):
        return video_data["transcription"]

    async def mock_get_response(self, prompt, message, *args, **kwargs):
        return OpenAIRecipe(
            name="Reel recipe",
            description="desc",
            ingredients=[OpenAIRecipeIngredient(text="flour")],
            instructions=[OpenAIRecipeInstruction(text="mix")],
        )

    monkeypatch.setattr(transcription, "download_video", mock_download_video)
    monkeypatch.setattr(transcription, "resolve_transcription", mock_resolve_transcription)
    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    strategy = RecipeScraperOpenAITranscription(
        SHARE_URL,
        get_locale_provider(),
        MagicMock(),
        resolved_url=REEL_URL,
    )
    recipe, extras = await strategy.parse()

    assert downloaded == [REEL_URL]
    assert recipe is not None
    assert recipe.org_url == SHARE_URL
    assert extras is not None


@pytest.mark.asyncio
async def test_scrape_passes_landing_url_to_strategies(monkeypatch: pytest.MonkeyPatch):
    seen: list[str | None] = []

    class CaptureStrategy(ABCScraperStrategy):
        def can_scrape(self) -> bool:
            seen.append(self.resolved_url)
            return False

        async def get_html(self, url: str) -> str:
            return ""

        async def parse(self, on_progress=None):
            return None, None

    async def mock_resilient_fetch(url: str) -> FetchResult:
        return _html_fetch(REEL_URL)

    monkeypatch.setattr(recipe_scraper_module, "resilient_fetch", mock_resilient_fetch)

    scraper = RecipeScraper(MagicMock(), get_locale_provider(), scrapers=[CaptureStrategy])
    await scraper.scrape(SHARE_URL)

    assert seen == [REEL_URL]


@pytest.mark.asyncio
async def test_scrape_without_fetch_does_not_invent_a_landing_url():
    seen: list[str | None] = []

    class CaptureStrategy(ABCScraperStrategy):
        def can_scrape(self) -> bool:
            seen.append(self.resolved_url)
            return False

        async def get_html(self, url: str) -> str:
            return ""

        async def parse(self, on_progress=None):
            return None, None

    scraper = RecipeScraper(MagicMock(), get_locale_provider(), scrapers=[CaptureStrategy])
    await scraper.scrape(SHARE_URL, html="<html></html>")

    assert seen == [None]
