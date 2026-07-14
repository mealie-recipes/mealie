import json
from pathlib import Path

from fastapi.testclient import TestClient

from mealie.core.config import get_app_settings
from mealie.schema.codex.social_recipe import SocialRecipe, SocialRecipeIngredient, SocialRecipeInstruction
from mealie.services.codex_cli import CodexCLIService
from mealie.services.scraper.scraper_strategies import RecipeScraperSocialMedia
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser
from tests.utils.helpers import parse_sse_events

SOCIAL_URL = "https://www.instagram.com/reel/example/"


def _make_social_recipe() -> SocialRecipe:
    return SocialRecipe(
        name=random_string(),
        description=random_string(),
        sourceUrl=SOCIAL_URL,
        servings=4,
        prepTimeMinutes=10,
        cookTimeMinutes=20,
        ingredients=[
            SocialRecipeIngredient(
                originalText="1 cup rice",
                quantity=1,
                unit="cup",
                food="rice",
                note=None,
            )
        ],
        instructions=[SocialRecipeInstruction(title=None, text="Cook the rice.")],
        tags=["social"],
        warnings=["Caption omitted salt quantity."],
        confidence="medium",
    )


def test_create_recipe_from_social_url_with_codex(
    api_client: TestClient,
    monkeypatch,
    unique_user: TestUser,
):
    social_recipe = _make_social_recipe()

    monkeypatch.setattr(RecipeScraperSocialMedia, "can_scrape", lambda self: True)

    def mock_download_audio(self, temp_path: Path):
        return {
            "audio": temp_path / "mealie.mp3",
            "subtitle": None,
            "title": "Social rice",
            "description": "1 cup rice\nCook the rice.",
            "thumbnail_url": None,
            "transcription": "",
        }

    async def mock_extract_structured(self, raw_content: str, schema_model):
        assert "Social rice" in raw_content
        assert schema_model is SocialRecipe
        return social_recipe

    monkeypatch.setattr(RecipeScraperSocialMedia, "_download_audio", mock_download_audio)
    monkeypatch.setattr(CodexCLIService, "extract_structured", mock_extract_structured)

    response = api_client.post(
        api_routes.recipes_create_social,
        json={"url": SOCIAL_URL, "include_tags": True},
        headers=unique_user.token,
    )
    assert response.status_code == 201

    slug = json.loads(response.text)
    recipe_response = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert recipe_response.status_code == 200

    recipe = recipe_response.json()
    assert recipe["name"] == social_recipe.name
    assert recipe["orgURL"] == SOCIAL_URL
    assert recipe["recipeServings"] == 4
    assert recipe["prepTime"] == "10 minutes"
    assert recipe["performTime"] == "20 minutes"
    ingredient = recipe["recipeIngredient"][0]
    assert ingredient["quantity"] == 1
    assert ingredient["note"] == "cup rice"
    assert ingredient["originalText"] == "1 cup rice"
    assert recipe["recipeInstructions"][0]["text"] == "Cook the rice."
    assert recipe["tags"][0]["name"] == "social"
    assert recipe["notes"][0]["title"] == "Import warning"


def test_create_recipe_from_social_url_streams_progress(
    api_client: TestClient,
    monkeypatch,
    unique_user: TestUser,
):
    social_recipe = _make_social_recipe()

    monkeypatch.setattr(RecipeScraperSocialMedia, "can_scrape", lambda self: True)
    monkeypatch.setattr(
        RecipeScraperSocialMedia,
        "_download_audio",
        lambda self, temp_path: {
            "audio": temp_path / "mealie.mp3",
            "subtitle": None,
            "title": "Social rice",
            "description": "1 cup rice\nCook the rice.",
            "thumbnail_url": None,
            "transcription": "",
        },
    )

    async def mock_extract_structured(self, raw_content: str, schema_model):
        return social_recipe

    monkeypatch.setattr(CodexCLIService, "extract_structured", mock_extract_structured)

    response = api_client.post(
        api_routes.recipes_create_social_stream,
        json={"url": SOCIAL_URL},
        headers=unique_user.token,
    )
    assert response.status_code == 200

    events = parse_sse_events(response.text)
    event_types = [event["event"] for event in events]
    assert "progress" in event_types
    assert "done" in event_types


def test_social_import_passes_configured_cookie_file_to_ytdlp(tmp_path: Path, monkeypatch):
    cookie_file = tmp_path / "instagram-cookies.txt"
    cookie_file.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    monkeypatch.setenv("SOCIAL_IMPORT_COOKIES_FILE", str(cookie_file))
    get_app_settings.cache_clear()

    captured_opts = {}

    class MockYoutubeDL:
        def __init__(self, opts):
            captured_opts.update(opts)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def extract_info(self, url: str, download: bool):
            return {
                "title": "Cookie-backed reel",
                "description": "caption",
                "thumbnail": None,
            }

    monkeypatch.setattr("mealie.services.scraper.scraper_strategies.yt_dlp.YoutubeDL", MockYoutubeDL)

    scraper = RecipeScraperSocialMedia.__new__(RecipeScraperSocialMedia)
    scraper.url = SOCIAL_URL

    try:
        video_data = scraper._download_audio(tmp_path)
    finally:
        get_app_settings.cache_clear()

    assert captured_opts["cookiefile"] == str(cookie_file)
    assert video_data["title"] == "Cookie-backed reel"
