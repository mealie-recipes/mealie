import json
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import mealie.services.openai.transcription as transcription_module
import mealie.services.recipe.import_workflow.steps.compile_source as compile_source_module
from mealie.core import exceptions
from mealie.schema.group.ai_providers import AIProviderCreate, AIProviderSettingsUpdate
from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.schema.openai.recipe import (
    OpenAIRecipe,
    OpenAIRecipeIngredient,
    OpenAIRecipeInstruction,
    OpenAIRecipeNotes,
    OpenAIRecipeNutrition,
)
from mealie.services.openai import OpenAIService
from mealie.services.recipe.recipe_data_service import RecipeDataService
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser
from tests.utils.helpers import parse_sse_events

VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture(autouse=True)
def ai_providers(unique_user: TestUser) -> Generator[None, None, None]:
    """Enable both the default and image providers, restoring the original settings afterwards."""

    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(
            default_provider_id=provider.id,
            audio_provider_id=provider.id,
            image_provider_id=provider.id,
        ),
    )

    yield

    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None),
    )


@pytest.fixture(autouse=True)
def no_image_downloads(monkeypatch: pytest.MonkeyPatch):
    async def mock_scrape_image(*_, **__) -> str:
        return "TEST_IMAGE"

    monkeypatch.setattr(RecipeDataService, "scrape_image", mock_scrape_image)


@pytest.fixture()
def recipe_name() -> str:
    return random_string()


@pytest.fixture()
def openai_recipe(recipe_name: str) -> OpenAIRecipe:
    return OpenAIRecipe(
        name=recipe_name,
        description=random_string(),
        recipe_yield="4 servings",
        total_time="1 hour",
        ingredients=[
            OpenAIRecipeIngredient(title="For the sauce", text=random_string()),
            OpenAIRecipeIngredient(text=random_string()),
        ],
        instructions=[
            OpenAIRecipeInstruction(title="Prep", text=random_string()),
            OpenAIRecipeInstruction(text=random_string()),
        ],
        notes=[OpenAIRecipeNotes(text=random_string())],
        nutrition=OpenAIRecipeNutrition(calories="250", protein_content="12 g"),
    )


class AIResponses:
    """Stands in for the AI provider, recording which response schemas were asked for."""

    def __init__(
        self,
        recipe: OpenAIRecipe | None = None,
        compiled: OpenAICompiledSource | None = None,
    ) -> None:
        self.recipe = recipe
        self.compiled = compiled or OpenAICompiledSource(
            contains_recipe=True, content=random_string(), language=None, image_url=None
        )
        self.requested_schemas: list[str] = []

    def install(self, monkeypatch: pytest.MonkeyPatch) -> "AIResponses":
        responses = self

        async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
            responses.requested_schemas.append(response_schema.__name__)
            if response_schema is OpenAICompiledSource:
                return responses.compiled
            if response_schema is OpenAIRecipe:
                return responses.recipe

            return None

        monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)
        return self


def post_ai(api_client: TestClient, user: TestUser, data: dict | None = None, files: list | None = None):
    return api_client.post(
        api_routes.recipes_create_ai,
        data=data or {},
        files=files,
        headers=user.token,
    )


def test_create_from_content(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    recipe_name: str,
):
    ai = AIResponses(recipe=openai_recipe).install(monkeypatch)

    r = post_ai(api_client, unique_user, {"content": "Grandma's pancakes\n2 cups flour\nMix and fry."})
    assert r.status_code == 201

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name

    # plain text is compiled without an AI call, so only the build step should hit the provider
    assert ai.requested_schemas == ["OpenAIRecipe"]


def test_create_from_ld_json_skips_the_compile_call(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    ai = AIResponses(recipe=openai_recipe).install(monkeypatch)

    ld_json = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": random_string(),
            "recipeIngredient": [random_string()],
        }
    )

    r = post_ai(api_client, unique_user, {"content": ld_json})
    assert r.status_code == 201
    assert ai.requested_schemas == ["OpenAIRecipe"]


def test_create_from_images(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    test_image_jpg: str,
):
    ai = AIResponses(recipe=openai_recipe).install(monkeypatch)

    with open(test_image_jpg, "rb") as f:
        r = post_ai(api_client, unique_user, files=[("images", ("recipe.jpg", f, "image/jpeg"))])

    assert r.status_code == 201
    slug = json.loads(r.text)

    # images have to be read by the provider, so both steps make a call
    assert ai.requested_schemas == ["OpenAICompiledSource", "OpenAIRecipe"]

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    r = api_client.get(
        api_routes.media_recipes_recipe_id_images_file_name(recipe["id"], "original.webp"),
        headers=unique_user.token,
    )
    assert r.status_code == 200


def test_create_from_content_and_images(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    test_image_jpg: str,
):
    ai = AIResponses(recipe=openai_recipe).install(monkeypatch)

    with open(test_image_jpg, "rb") as f:
        r = post_ai(
            api_client,
            unique_user,
            data={"content": random_string()},
            files=[("images", ("recipe.jpg", f, "image/jpeg"))],
        )

    assert r.status_code == 201
    assert ai.requested_schemas == ["OpenAICompiledSource", "OpenAIRecipe"]


def test_create_from_url(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    recipe_name: str,
):
    AIResponses(recipe=openai_recipe).install(monkeypatch)

    url = f"https://example.com/recipe/{random_string()}"
    ld_json = json.dumps({"@context": "https://schema.org", "@type": "Recipe", "name": random_string()})
    html = f'<html><head><script type="application/ld+json">{ld_json}</script></head><body>Recipe</body></html>'

    async def mock_safe_scrape_html(_: str) -> str:
        return html

    monkeypatch.setattr(compile_source_module, "safe_scrape_html", mock_safe_scrape_html)

    r = post_ai(api_client, unique_user, {"url": url})
    assert r.status_code == 201

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name
    assert recipe["orgURL"] == url


def test_create_from_video_url(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    recipe_name: str,
):
    ai = AIResponses(recipe=openai_recipe).install(monkeypatch)

    def mock_download_video(url: str, temp_path: Path):
        return {
            "audio": temp_path / "mealie.mp3",
            "subtitle": None,
            "title": random_string(),
            "description": random_string(),
            "thumbnail_url": "https://example.com/thumbnail.jpg",
            "transcription": random_string(),
        }

    async def fail_if_fetched(_: str) -> str:
        raise AssertionError("a video URL should be downloaded, not fetched as a webpage")

    monkeypatch.setattr(transcription_module, "download_video", mock_download_video)
    monkeypatch.setattr(compile_source_module, "safe_scrape_html", fail_if_fetched)

    r = post_ai(api_client, unique_user, {"url": VIDEO_URL})
    assert r.status_code == 201

    # the transcript is already a faithful record, so only the build step hits the provider
    assert ai.requested_schemas == ["OpenAIRecipe"]

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name
    assert recipe["orgURL"] == VIDEO_URL


def test_create_from_video_url_without_audio_provider_falls_back_to_fetching(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    settings = unique_user.repos.group_ai_provider_settings.get_one(unique_user.repos.group_id)
    assert settings
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(
            default_provider_id=settings.default_provider_id,
            audio_provider_id=None,
            image_provider_id=settings.image_provider_id,
        ),
    )

    AIResponses(recipe=openai_recipe).install(monkeypatch)

    fetched: list[str] = []

    async def mock_safe_scrape_html(url: str) -> str:
        fetched.append(url)
        return f"<html><body>{random_string()}</body></html>"

    monkeypatch.setattr(compile_source_module, "safe_scrape_html", mock_safe_scrape_html)

    r = post_ai(api_client, unique_user, {"url": VIDEO_URL})
    assert r.status_code == 201
    assert fetched == [VIDEO_URL]


def test_create_surfaces_rate_limit_errors(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
):
    async def mock_get_response(self, prompt, message, *args, **kwargs):
        raise exceptions.RateLimitError("429 too many requests")

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = post_ai(api_client, unique_user, {"content": random_string()})
    assert r.status_code == 400
    assert "rate limiting" in r.text


def test_create_preserves_sections_and_nutrition(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    AIResponses(recipe=openai_recipe).install(monkeypatch)

    r = post_ai(api_client, unique_user, {"content": random_string()})
    assert r.status_code == 201

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()

    assert [i["title"] for i in recipe["recipeIngredient"]] == ["For the sauce", None]
    assert [i["title"] for i in recipe["recipeInstructions"]] == ["Prep", None]
    assert recipe["nutrition"]["calories"] == "250"
    assert recipe["nutrition"]["proteinContent"] == "12"


def test_create_translates_when_requested(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    messages: list[str] = []

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        messages.append(message)
        return openai_recipe if response_schema is OpenAIRecipe else None

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = post_ai(api_client, unique_user, {"content": random_string(), "translateLanguage": "French"})
    assert r.status_code == 201
    assert any("French" in message for message in messages)


def test_create_with_no_source_is_rejected(api_client: TestClient, unique_user: TestUser):
    r = post_ai(api_client, unique_user, {})
    assert r.status_code == 400


def test_create_when_source_has_no_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    test_image_jpg: str,
):
    compiled = OpenAICompiledSource(contains_recipe=False, content="", language=None, image_url=None)
    AIResponses(compiled=compiled).install(monkeypatch)

    with open(test_image_jpg, "rb") as f:
        r = post_ai(api_client, unique_user, files=[("images", ("not-a-recipe.jpg", f, "image/jpeg"))])

    assert r.status_code == 400


def test_create_when_provider_returns_nothing(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
):
    AIResponses(recipe=None).install(monkeypatch)

    r = post_ai(api_client, unique_user, {"content": random_string()})
    assert r.status_code == 400


def test_create_with_ai_disabled(api_client: TestClient, unique_user: TestUser):
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(default_provider_id=None, audio_provider_id=None, image_provider_id=None),
    )

    r = post_ai(api_client, unique_user, {"content": random_string()})
    assert r.status_code == 400


def test_create_with_images_but_no_image_provider(
    api_client: TestClient,
    unique_user: TestUser,
    test_image_jpg: str,
):
    settings = unique_user.repos.group_ai_provider_settings.get_one(unique_user.repos.group_id)
    assert settings
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(
            default_provider_id=settings.default_provider_id,
            audio_provider_id=None,
            image_provider_id=None,
        ),
    )

    with open(test_image_jpg, "rb") as f:
        r = post_ai(api_client, unique_user, files=[("images", ("recipe.jpg", f, "image/jpeg"))])

    assert r.status_code == 400


def test_create_stream_emits_progress(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    test_image_jpg: str,
):
    AIResponses(recipe=openai_recipe).install(monkeypatch)

    with open(test_image_jpg, "rb") as f:
        r = api_client.post(
            api_routes.recipes_create_ai_stream,
            files=[("images", ("recipe.jpg", f, "image/jpeg"))],
            headers=unique_user.token,
        )

    assert r.status_code == 200
    events = parse_sse_events(r.text)
    event_types = [e["event"] for e in events]

    assert "done" in event_types
    assert "progress" in event_types


def test_create_stream_emits_error(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
):
    AIResponses(recipe=None).install(monkeypatch)

    r = api_client.post(
        api_routes.recipes_create_ai_stream,
        data={"content": random_string()},
        headers=unique_user.token,
    )

    assert r.status_code == 200
    events = parse_sse_events(r.text)
    assert [e["event"] for e in events][-1] == "error"
