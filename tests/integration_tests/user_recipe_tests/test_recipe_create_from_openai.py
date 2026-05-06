import json

import pytest
from fastapi.testclient import TestClient

import mealie.services.scraper.recipe_scraper as recipe_scraper_module
import mealie.services.scraper.scraper_strategies as scraper_strategies_module
from mealie.schema.openai.general import OpenAIText
from mealie.services.openai import OpenAIService
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper.scraper_strategies import RecipeScraperOpenAI
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser
from tests.utils.helpers import parse_sse_events


@pytest.fixture()
def recipe_name() -> str:
    return random_string()


@pytest.fixture()
def recipe_ld_json(recipe_name: str) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": recipe_name,
            "recipeIngredient": [random_string() for _ in range(3)],
            "recipeInstructions": [
                {"@type": "HowToStep", "text": random_string()},
                {"@type": "HowToStep", "text": random_string()},
            ],
        }
    )


@pytest.fixture()
def bare_html() -> str:
    return f"<html><body><p>{random_string()}</p></body></html>"


@pytest.fixture()
def recipe_url() -> str:
    return f"https://example.com/recipe/{random_string()}"


@pytest.fixture(autouse=True)
def openai_scraper_setup(monkeypatch: pytest.MonkeyPatch, bare_html: str):
    """Restrict to only RecipeScraperOpenAI, enable it unconditionally, and prevent real HTTP calls."""
    monkeypatch.setattr(recipe_scraper_module, "DEFAULT_SCRAPER_STRATEGIES", [RecipeScraperOpenAI])

    settings_stub = type("_Settings", (), {"OPENAI_ENABLED": True})()
    monkeypatch.setattr(scraper_strategies_module, "get_app_settings", lambda: settings_stub)

    async def mock_safe_scrape_html(url: str) -> str:
        return bare_html

    monkeypatch.setattr(recipe_scraper_module, "safe_scrape_html", mock_safe_scrape_html)
    monkeypatch.setattr(RecipeDataService, "scrape_image", lambda *_: "TEST_IMAGE")


def test_create_by_url_via_openai(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    recipe_ld_json: str,
    recipe_url: str,
    recipe_name: str,
):
    async def mock_get_response(self, prompt, message, *args, **kwargs) -> OpenAIText | None:
        return OpenAIText(text=recipe_ld_json)

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    api_client.delete(api_routes.recipes_slug("openai-test-cake"), headers=unique_user.token)
    response = api_client.post(
        api_routes.recipes_create_url,
        json={"url": recipe_url, "include_tags": False},
        headers=unique_user.token,
    )

    assert response.status_code == 201
    slug = json.loads(response.text)

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name
    assert len(recipe["recipeIngredient"]) == 3
    assert len(recipe["recipeInstructions"]) == 2


def test_create_by_html_or_json_via_openai(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    recipe_ld_json: str,
    bare_html: str,
    recipe_name: str,
):
    async def mock_get_response(self, prompt, message, *args, **kwargs) -> OpenAIText | None:
        return OpenAIText(text=recipe_ld_json)

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    api_client.delete(api_routes.recipes_slug("openai-test-cake"), headers=unique_user.token)
    response = api_client.post(
        api_routes.recipes_create_html_or_json,
        json={"data": bare_html, "include_tags": False},
        headers=unique_user.token,
    )

    assert response.status_code == 201
    slug = json.loads(response.text)

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name


def test_create_stream_via_openai_emits_progress(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    recipe_ld_json: str,
    bare_html: str,
):
    async def mock_get_response(self, prompt, message, *args, **kwargs) -> OpenAIText | None:
        return OpenAIText(text=recipe_ld_json)

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    api_client.delete(api_routes.recipes_slug("openai-test-cake"), headers=unique_user.token)
    response = api_client.post(
        api_routes.recipes_create_html_or_json_stream,
        json={"data": bare_html, "include_tags": False},
        headers=unique_user.token,
    )

    assert response.status_code == 200
    events = parse_sse_events(response.text)
    event_types = [e["event"] for e in events]

    assert "done" in event_types
    assert any(e["event"] == "progress" for e in events)


def test_create_by_url_openai_returns_none(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    recipe_url: str,
):
    """When OpenAI returns None the endpoint should return 400."""

    async def mock_get_response(self, prompt, message, *args, **kwargs) -> OpenAIText | None:
        return None

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    response = api_client.post(
        api_routes.recipes_create_url,
        json={"url": recipe_url, "include_tags": False},
        headers=unique_user.token,
    )
    assert response.status_code == 400


def test_create_by_url_openai_disabled(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    recipe_url: str,
):
    """When OPENAI_ENABLED is False, can_scrape() returns False and the endpoint returns 400."""
    disabled_settings = type("_Settings", (), {"OPENAI_ENABLED": False})()
    monkeypatch.setattr(scraper_strategies_module, "get_app_settings", lambda: disabled_settings)

    response = api_client.post(
        api_routes.recipes_create_url,
        json={"url": recipe_url, "include_tags": False},
        headers=unique_user.token,
    )
    assert response.status_code == 400
