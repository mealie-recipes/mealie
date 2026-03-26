import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import mealie.services.scraper.recipe_scraper as recipe_scraper_module
from mealie.core import exceptions
from mealie.core.config import get_app_settings
from mealie.schema.openai.recipe import OpenAIRecipe, OpenAIRecipeIngredient, OpenAIRecipeInstruction
from mealie.services.openai import OpenAIService
from mealie.services.scraper.scraper_strategies import RecipeScraperOpenAITranscription
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser

VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def _make_openai_recipe() -> OpenAIRecipe:
    return OpenAIRecipe(
        name=random_string(),
        description=random_string(),
        ingredients=[OpenAIRecipeIngredient(text=random_string()) for _ in range(random_int(2, 5))],
        instructions=[OpenAIRecipeInstruction(text=random_string()) for _ in range(random_int(2, 5))],
    )


@pytest.fixture(autouse=True)
def video_scraper_setup(monkeypatch: pytest.MonkeyPatch):
    # Restrict to only the video scraper so other strategies don't interfere
    monkeypatch.setattr(recipe_scraper_module, "DEFAULT_SCRAPER_STRATEGIES", [RecipeScraperOpenAITranscription])

    # Prevent any real HTTP calls during scraping
    async def mock_safe_scrape_html(url: str) -> str:
        return "<html></html>"

    monkeypatch.setattr(recipe_scraper_module, "safe_scrape_html", mock_safe_scrape_html)


def test_create_recipe_from_video(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
):
    openai_recipe = _make_openai_recipe()

    def mock_download_audio(self, temp_path: Path):
        return {
            "audio": temp_path / "mealie.mp3",
            "subtitle": None,
            "title": random_string(),
            "description": random_string(),
            "thumbnail_url": "https://example.com/thumbnail.jpg",
            "transcription": random_string(),
        }

    async def mock_get_response(self, prompt, message, *args, **kwargs) -> OpenAIRecipe | None:
        return openai_recipe

    monkeypatch.setattr(RecipeScraperOpenAITranscription, "_download_audio", mock_download_audio)
    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = api_client.post(api_routes.recipes_create_url, json={"url": VIDEO_URL}, headers=unique_user.token)
    assert r.status_code == 201

    slug = json.loads(r.text)
    r = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert r.status_code == 200

    recipe = r.json()
    assert recipe["name"] == openai_recipe.name
    assert len(recipe["recipeIngredient"]) == len(openai_recipe.ingredients)
    assert len(recipe["recipeInstructions"]) == len(openai_recipe.instructions)


def test_create_recipe_from_video_uses_subtitle_over_transcription(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
    tmp_path: Path,
):
    openai_recipe = _make_openai_recipe()

    subtitle_text = random_string()
    subtitle_file = tmp_path / "mealie.en.vtt"
    subtitle_file.write_text(f"WEBVTT\n\n1\n00:00:01.000 --> 00:00:03.000\n{subtitle_text}\n")

    def mock_download_audio(self, temp_path: Path):
        return {
            "audio": temp_path / "mealie.mp3",
            "subtitle": subtitle_file,
            "title": random_string(),
            "description": random_string(),
            "thumbnail_url": None,
            "transcription": "",
        }

    # transcribe_audio must NOT be called when a subtitle is available
    async def mock_transcribe_audio(self, audio_file_path: Path) -> str | None:
        raise AssertionError("transcribe_audio should not be called when subtitles are available")

    async def mock_get_response(self, prompt, message, *args, **kwargs) -> OpenAIRecipe | None:
        assert subtitle_text in message
        return openai_recipe

    monkeypatch.setattr(RecipeScraperOpenAITranscription, "_download_audio", mock_download_audio)
    monkeypatch.setattr(OpenAIService, "transcribe_audio", mock_transcribe_audio)
    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = api_client.post(api_routes.recipes_create_url, json={"url": VIDEO_URL}, headers=unique_user.token)
    assert r.status_code == 201


def test_create_recipe_from_video_transcription_disabled(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
):
    settings = get_app_settings()
    monkeypatch.setattr(settings, "OPENAI_ENABLE_TRANSCRIPTION_SERVICES", False)

    r = api_client.post(api_routes.recipes_create_url, json={"url": VIDEO_URL}, headers=unique_user.token)
    assert r.status_code == 400


def test_create_recipe_from_video_download_error(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
):
    def mock_download_audio(self, temp_path: Path):
        raise exceptions.VideoDownloadError("Mock video download error")

    monkeypatch.setattr(RecipeScraperOpenAITranscription, "_download_audio", mock_download_audio)

    r = api_client.post(api_routes.recipes_create_url, json={"url": VIDEO_URL}, headers=unique_user.token)
    assert r.status_code == 400


def test_create_recipe_from_video_transcription_error(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
):
    def mock_download_audio(self, temp_path: Path):
        return {
            "audio": temp_path / "mealie.mp3",
            "subtitle": None,
            "title": random_string(),
            "description": random_string(),
            "thumbnail_url": None,
            "transcription": "",
        }

    async def mock_transcribe_audio(self, audio_file_path: Path) -> str | None:
        raise Exception("Mock transcribe audio exception")

    monkeypatch.setattr(RecipeScraperOpenAITranscription, "_download_audio", mock_download_audio)
    monkeypatch.setattr(OpenAIService, "transcribe_audio", mock_transcribe_audio)

    r = api_client.post(api_routes.recipes_create_url, json={"url": VIDEO_URL}, headers=unique_user.token)
    assert r.status_code == 400


def test_create_recipe_from_video_empty_openai_response(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
):
    def mock_download_audio(self, temp_path: Path):
        return {
            "audio": temp_path / "mealie.mp3",
            "subtitle": None,
            "title": random_string(),
            "description": random_string(),
            "thumbnail_url": None,
            "transcription": random_string(),
        }

    async def mock_get_response(self, prompt, message, *args, **kwargs) -> OpenAIRecipe | None:
        return None

    monkeypatch.setattr(RecipeScraperOpenAITranscription, "_download_audio", mock_download_audio)
    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = api_client.post(api_routes.recipes_create_url, json={"url": VIDEO_URL}, headers=unique_user.token)
    assert r.status_code == 400
