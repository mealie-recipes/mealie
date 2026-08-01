import json

import pytest
from fastapi.testclient import TestClient

import mealie.services.scraper.recipe_scraper as recipe_scraper_module
from mealie.schema.codex.social_recipe import SocialRecipe, SocialRecipeIngredient, SocialRecipeInstruction
from mealie.schema.group.ai_providers import AIProviderCreate, AIProviderSettingsUpdate
from mealie.services.codex_cli import CodexCLIError, CodexCLIService
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
def codex_recipe(recipe_name: str) -> SocialRecipe:
    return SocialRecipe(
        name=recipe_name,
        description=None,
        sourceUrl=None,
        imageUrl=None,
        servings=None,
        totalTimeMinutes=None,
        prepTimeMinutes=None,
        cookTimeMinutes=None,
        ingredients=[
            SocialRecipeIngredient(
                originalText=random_string(),
                quantity=None,
                unit=None,
                food=random_string(),
                foodId=None,
                unitId=None,
                note=None,
            )
            for _ in range(3)
        ],
        instructions=[
            SocialRecipeInstruction(title=None, text=random_string()),
            SocialRecipeInstruction(title=None, text=random_string()),
        ],
        tags=[],
        warnings=[],
        confidence="high",
    )


@pytest.fixture()
def bare_html() -> str:
    return f"<html><body><p>{random_string()}</p></body></html>"


@pytest.fixture()
def recipe_url() -> str:
    return f"https://example.com/recipe/{random_string()}"


@pytest.fixture(autouse=True)
def openai_scraper_setup(monkeypatch: pytest.MonkeyPatch, bare_html: str, unique_user: TestUser):
    """Restrict to only RecipeScraperOpenAI, create real DB provider data, and prevent real HTTP calls."""
    monkeypatch.setattr(recipe_scraper_module, "DEFAULT_SCRAPER_STRATEGIES", [RecipeScraperOpenAI])

    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(default_provider_id=provider.id, audio_provider_id=None, image_provider_id=None),
    )

    async def mock_safe_scrape_html(url: str) -> str:
        return bare_html

    monkeypatch.setattr(recipe_scraper_module, "safe_scrape_html", mock_safe_scrape_html)
    monkeypatch.setattr(RecipeDataService, "scrape_image", lambda *_: "TEST_IMAGE")


def test_create_by_url_via_openai(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    codex_recipe: SocialRecipe,
    recipe_url: str,
    recipe_name: str,
):
    async def mock_extract_structured(self, raw_content: str, schema_model, prompt_context: str | None = None):
        assert schema_model is SocialRecipe
        assert prompt_context
        return codex_recipe

    monkeypatch.setattr(CodexCLIService, "extract_structured", mock_extract_structured)

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
    codex_recipe: SocialRecipe,
    bare_html: str,
    recipe_name: str,
):
    async def mock_extract_structured(self, raw_content: str, schema_model, prompt_context: str | None = None):
        assert schema_model is SocialRecipe
        assert prompt_context
        return codex_recipe

    monkeypatch.setattr(CodexCLIService, "extract_structured", mock_extract_structured)

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
    codex_recipe: SocialRecipe,
    bare_html: str,
):
    async def mock_extract_structured(self, raw_content: str, schema_model, prompt_context: str | None = None):
        return codex_recipe

    monkeypatch.setattr(CodexCLIService, "extract_structured", mock_extract_structured)

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

    async def mock_extract_structured(self, raw_content: str, schema_model, prompt_context: str | None = None):
        raise CodexCLIError("Codex returned no recipe")

    monkeypatch.setattr(CodexCLIService, "extract_structured", mock_extract_structured)

    response = api_client.post(
        api_routes.recipes_create_url,
        json={"url": recipe_url, "include_tags": False},
        headers=unique_user.token,
    )
    assert response.status_code == 400


def test_create_by_url_codex_failure_returns_400(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    recipe_url: str,
):
    """When Codex cannot extract a recipe, the endpoint returns 400."""

    async def mock_extract_structured(self, raw_content: str, schema_model, prompt_context: str | None = None):
        raise CodexCLIError("Codex CLI recipe extraction failed")

    monkeypatch.setattr(CodexCLIService, "extract_structured", mock_extract_structured)

    response = api_client.post(
        api_routes.recipes_create_url,
        json={"url": recipe_url, "include_tags": False},
        headers=unique_user.token,
    )
    assert response.status_code == 400
