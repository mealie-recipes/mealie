import json

import pytest
from fastapi.testclient import TestClient

import mealie.services.recipe.import_workflow.steps.compile_source as compile_source_module
import mealie.services.scraper.recipe_scraper as recipe_scraper_module
from mealie.schema.group.ai_providers import AIProviderCreate, AIProviderSettingsUpdate
from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.schema.openai.organizers import OpenAIOrganizers
from mealie.schema.openai.recipe import OpenAIRecipe, OpenAIRecipeIngredient, OpenAIRecipeInstruction
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
def openai_recipe(recipe_name: str) -> OpenAIRecipe:
    return OpenAIRecipe(
        name=recipe_name,
        description=random_string(),
        ingredients=[OpenAIRecipeIngredient(text=random_string()) for _ in range(3)],
        instructions=[OpenAIRecipeInstruction(text=random_string()) for _ in range(2)],
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


def mock_ai(
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe | None,
    organizers: OpenAIOrganizers | None = None,
) -> list[str]:
    """Installs a stand-in provider, returning the list of schemas it was asked for."""

    requested_schemas: list[str] = []

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        requested_schemas.append(response_schema.__name__)

        if response_schema is OpenAICompiledSource:
            return OpenAICompiledSource(contains_recipe=True, content=random_string(), language=None, image_url=None)
        if response_schema is OpenAIRecipe:
            return openai_recipe
        if response_schema is OpenAIOrganizers:
            return organizers

        return None

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)
    return requested_schemas


def test_create_by_url_via_openai(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    recipe_url: str,
    recipe_name: str,
):
    mock_ai(monkeypatch, openai_recipe)

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
    openai_recipe: OpenAIRecipe,
    bare_html: str,
    recipe_name: str,
):
    mock_ai(monkeypatch, openai_recipe)

    response = api_client.post(
        api_routes.recipes_create_html_or_json,
        json={"data": bare_html, "include_tags": False},
        headers=unique_user.token,
    )

    assert response.status_code == 201
    slug = json.loads(response.text)

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name


def test_supplied_html_is_not_fetched_again(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    bare_html: str,
    recipe_url: str,
    recipe_name: str,
):
    """
    HTML that arrives with a URL is that page's own content, not extra source material.

    The workflow compiles every source it's given, so passing the page as ordinary content would
    make it fetch the URL as well and compile the same page twice.
    """

    mock_ai(monkeypatch, openai_recipe)

    async def fail_if_fetched(_: str) -> str:
        raise AssertionError("the page was supplied by the caller, so it should not be fetched")

    monkeypatch.setattr(compile_source_module, "safe_scrape_html", fail_if_fetched)

    response = api_client.post(
        api_routes.recipes_create_html_or_json,
        json={"data": bare_html, "url": recipe_url, "include_tags": False},
        headers=unique_user.token,
    )

    assert response.status_code == 201
    slug = json.loads(response.text)

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name
    assert recipe["orgURL"] == recipe_url


def test_organizers_are_not_requested_unless_they_are_wanted(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    recipe_url: str,
):
    requested_schemas = mock_ai(monkeypatch, openai_recipe)

    response = api_client.post(
        api_routes.recipes_create_url,
        json={"url": recipe_url, "include_tags": False, "include_categories": False},
        headers=unique_user.token,
    )

    assert response.status_code == 201
    assert "OpenAIOrganizers" not in requested_schemas


def test_tags_are_imported_when_requested(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    recipe_url: str,
):
    tag_name = random_string()
    requested_schemas = mock_ai(monkeypatch, openai_recipe, OpenAIOrganizers(tags=[tag_name]))

    response = api_client.post(
        api_routes.recipes_create_url,
        json={"url": recipe_url, "include_tags": True},
        headers=unique_user.token,
    )

    assert response.status_code == 201
    assert "OpenAIOrganizers" in requested_schemas

    slug = json.loads(response.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert [tag["name"] for tag in recipe["tags"]] == [tag_name.title()]


def test_create_stream_via_openai_emits_progress(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    bare_html: str,
):
    mock_ai(monkeypatch, openai_recipe)

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
    """When the provider returns nothing the endpoint should return 400."""

    mock_ai(monkeypatch, None)

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
    """When no default provider is set, can_scrape() returns False and the endpoint returns 400."""
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None),
    )

    response = api_client.post(
        api_routes.recipes_create_url,
        json={"url": recipe_url, "include_tags": False},
        headers=unique_user.token,
    )
    assert response.status_code == 400
