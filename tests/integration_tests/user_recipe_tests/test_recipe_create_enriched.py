import json

import pytest
from fastapi.testclient import TestClient

import mealie.services.scraper.recipe_scraper as recipe_scraper_module
from mealie.schema.group.ai_providers import AIProviderCreate, AIProviderSettingsUpdate
from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.schema.openai.organizers import OpenAIOrganizers
from mealie.schema.openai.recipe import (
    OpenAIInstructionEnrichment,
    OpenAIInstructionEnrichments,
    OpenAIRecipe,
    OpenAIRecipeIngredient,
    OpenAIRecipeInstruction,
)
from mealie.services.openai import OpenAIService
from mealie.services.recipe.import_workflow import RecipeImportWorkflow
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper.scraper_strategies import RecipeScraperOpenAI
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def set_enrichment(user: TestUser, enabled: bool, with_provider: bool = True) -> None:
    provider_id = None
    if with_provider:
        provider_id = user.repos.group_ai_providers.create(
            AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
        ).id

    user.repos.group_ai_provider_settings.update(
        user.repos.group_id,
        AIProviderSettingsUpdate(
            default_provider_id=provider_id,
            audio_provider_id=None,
            image_provider_id=None,
            enrich_non_ai_imports=enabled,
        ),
    )


def mock_ai(
    monkeypatch: pytest.MonkeyPatch,
    organizers: OpenAIOrganizers | None = None,
    openai_recipe: OpenAIRecipe | None = None,
) -> list[str]:
    """Installs a stand-in provider, returning the list of schemas it was asked for."""

    requested_schemas: list[str] = []

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        requested_schemas.append(response_schema.__name__)

        if response_schema is OpenAIInstructionEnrichments:
            return OpenAIInstructionEnrichments(instructions=[OpenAIInstructionEnrichment(step=1, ingredients=[1])])
        if response_schema is OpenAIOrganizers:
            return organizers
        if response_schema is OpenAICompiledSource:
            return OpenAICompiledSource(contains_recipe=True, content=random_string(), language=None, image_url=None)
        if response_schema is OpenAIRecipe:
            return openai_recipe

        return None

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)
    return requested_schemas


def schema_recipe(name: str, keywords: str = "") -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": name,
            "keywords": keywords,
            "recipeIngredient": ["1 cup flour", "2 eggs"],
            "recipeInstructions": [{"@type": "HowToStep", "text": "Mix the flour and eggs."}],
        }
    )


def import_recipe(api_client: TestClient, user: TestUser, data: str, include_tags: bool = False) -> dict:
    response = api_client.post(
        api_routes.recipes_create_html_or_json,
        json={"data": data, "include_tags": include_tags},
        headers=user.token,
    )
    assert response.status_code == 201

    slug = json.loads(response.text)
    return api_client.get(api_routes.recipes_slug(slug), headers=user.token).json()


@pytest.fixture(autouse=True)
def no_image_downloads(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(RecipeDataService, "scrape_image", lambda *_: "TEST_IMAGE")


def test_scraped_recipe_is_enriched_when_enabled(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    set_enrichment(unique_user, enabled=True)
    requested_schemas = mock_ai(monkeypatch)

    recipe = import_recipe(api_client, unique_user, schema_recipe(random_string()))

    assert requested_schemas == ["OpenAIInstructionEnrichments"]
    first_ingredient = recipe["recipeIngredient"][0]["referenceId"]
    assert recipe["recipeInstructions"][0]["ingredientReferences"] == [{"referenceId": first_ingredient}]


@pytest.mark.parametrize("with_provider", [True, False])
def test_scraped_recipe_is_not_enriched_when_disabled(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch, with_provider: bool
):
    # without a default provider the setting has no effect, even if it's switched on
    set_enrichment(unique_user, enabled=not with_provider, with_provider=with_provider)
    requested_schemas = mock_ai(monkeypatch)

    recipe = import_recipe(api_client, unique_user, schema_recipe(random_string()))

    assert requested_schemas == []
    assert recipe["recipeInstructions"][0]["ingredientReferences"] == []


def test_ai_organizers_replace_the_pages_own(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    set_enrichment(unique_user, enabled=True)
    tag_name = random_string()
    requested_schemas = mock_ai(monkeypatch, OpenAIOrganizers(tags=[tag_name]))

    recipe = import_recipe(api_client, unique_user, schema_recipe(random_string(), keywords="page-tag"), True)

    assert "OpenAIOrganizers" in requested_schemas
    assert [tag["name"] for tag in recipe["tags"]] == [tag_name.title()]


@pytest.mark.parametrize("organizers", [None, OpenAIOrganizers()], ids=["no-response", "empty-lists"])
def test_pages_organizers_are_kept_when_ai_returns_none(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    organizers: OpenAIOrganizers | None,
):
    set_enrichment(unique_user, enabled=True)
    mock_ai(monkeypatch, organizers=organizers)

    recipe = import_recipe(api_client, unique_user, schema_recipe(random_string(), keywords="page-tag"), True)

    assert [tag["name"] for tag in recipe["tags"]] == ["Page-Tag"]


def test_failed_enrichment_keeps_the_scraped_recipe(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    set_enrichment(unique_user, enabled=True)
    mock_ai(monkeypatch)

    async def fail(*_, **__):
        raise RuntimeError("enrichment failed")

    monkeypatch.setattr(RecipeImportWorkflow, "run", fail)
    name = random_string()

    recipe = import_recipe(api_client, unique_user, schema_recipe(name))

    assert recipe["name"] == name
    assert len(recipe["recipeIngredient"]) == 2


def test_ai_scraped_recipe_is_not_enriched_twice(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(recipe_scraper_module, "DEFAULT_SCRAPER_STRATEGIES", [RecipeScraperOpenAI])
    set_enrichment(unique_user, enabled=True)
    requested_schemas = mock_ai(
        monkeypatch,
        openai_recipe=OpenAIRecipe(
            name=random_string(),
            ingredients=[OpenAIRecipeIngredient(text=random_string())],
            instructions=[OpenAIRecipeInstruction(text=random_string())],
        ),
    )

    import_recipe(api_client, unique_user, f"<html><body><p>{random_string()}</p></body></html>")

    assert requested_schemas.count("OpenAIInstructionEnrichments") == 1
