import json

import pytest
from fastapi.testclient import TestClient

from mealie.core.config import get_app_settings
from mealie.services.openai import OpenAIService
from mealie.services.recipe.recipe_service import OpenAIRecipeService
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def test_create_recipe_from_video(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
):
    # Mock Settings
    settings = get_app_settings()
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "mock-api-key")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo")
    monkeypatch.setattr(settings, "OPENAI_ENABLE_TRANSCRIPTION_SERVICES", True)

    # Mock _download_audio
    def mock_download_audio(self, video_url: str):
        return {
            "audio": "mock_audio_path",
            "subtitle": None,
            "title": "Mock Video Title",
            "description": "Mock Video Description",
            "thumbnail": "http://mock.thumbnail/url",
            "transcription": "Mock transcription of the video recipe.",
        }

    monkeypatch.setattr(OpenAIRecipeService, "_download_audio", mock_download_audio)

    # Mock OpenAI Response
    async def mock_get_response(self, prompt: str, message: str, *args, **kwargs) -> str | None:
        data = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": "Mock Recipe",
            "description": "Mock Description",
            "recipeIngredient": ["1 cup flour", "2 eggs"],
            "recipeInstructions": [
                {"@type": "HowToStep", "text": "Mix ingredients"},
                {"@type": "HowToStep", "text": "Bake"},
            ],
        }
        return json.dumps(data)

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    # Test Request
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    r = api_client.post(
        api_routes.recipes_create_video,
        json={"url": video_url},
        headers=unique_user.token,
    )

    assert r.status_code == 201

    # Verify Recipe Created
    slug = r.json()

    r = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert r.status_code == 200
    recipe = r.json()
    assert recipe["name"]
    assert len(recipe["recipeInstructions"]) > 0
    assert len(recipe["recipeIngredient"]) > 0
