import json
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from slugify import slugify

import mealie.services.openai.transcription as transcription_module
import mealie.services.recipe.import_workflow.steps.compile_source as compile_source_module
from mealie.core import exceptions
from mealie.lang import get_locale_provider
from mealie.schema.group.ai_providers import AIProviderCreate, AIProviderSettingsUpdate
from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.schema.openai.organizers import OpenAIOrganizers
from mealie.schema.openai.recipe import (
    OpenAIRecipe,
    OpenAIRecipeIngredient,
    OpenAIRecipeInstruction,
    OpenAIRecipeNotes,
    OpenAIRecipeNutrition,
)
from mealie.schema.recipe.recipe_category import TagSave
from mealie.services.openai import OpenAINotEnabledException, OpenAIService
from mealie.services.recipe.organizer_resolver import OrganizerResolver
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper.cleaner import NO_IMAGE
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser
from tests.utils.helpers import parse_sse_events

VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

translator = get_locale_provider("en-US")


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
        organizers: OpenAIOrganizers | None = None,
    ) -> None:
        self.recipe = recipe
        self.compiled = compiled or OpenAICompiledSource(
            contains_recipe=True, content=random_string(), language=None, image_url=None
        )
        self.organizers = organizers
        self.requested_schemas: list[str] = []
        self.prompts: list[str] = []
        self.messages: list[str] = []

    def install(self, monkeypatch: pytest.MonkeyPatch) -> "AIResponses":
        responses = self

        async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
            responses.requested_schemas.append(response_schema.__name__)
            responses.prompts.append(prompt)
            responses.messages.append(message)

            if response_schema is OpenAICompiledSource:
                return responses.compiled
            if response_schema is OpenAIRecipe:
                return responses.recipe
            if response_schema is OpenAIOrganizers:
                return responses.organizers

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
    assert "OpenAICompiledSource" not in ai.requested_schemas


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
    assert "OpenAICompiledSource" not in ai.requested_schemas


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
    assert ai.requested_schemas[:2] == ["OpenAICompiledSource", "OpenAIRecipe"]

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
    transcribed_images = random_string()
    pasted_content = random_string()

    ai = AIResponses(
        recipe=openai_recipe,
        compiled=OpenAICompiledSource(contains_recipe=True, content=transcribed_images, language=None, image_url=None),
    ).install(monkeypatch)

    with open(test_image_jpg, "rb") as f:
        r = post_ai(
            api_client,
            unique_user,
            data={"content": pasted_content},
            files=[("images", ("recipe.jpg", f, "image/jpeg"))],
        )

    assert r.status_code == 201
    assert ai.requested_schemas[:2] == ["OpenAICompiledSource", "OpenAIRecipe"]

    # the images and the pasted content are separate sources, and both reach the build step
    build_message = ai.messages[1]
    assert transcribed_images in build_message
    assert pasted_content in build_message


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
    assert "OpenAICompiledSource" not in ai.requested_schemas

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name
    assert recipe["orgURL"] == VIDEO_URL


def test_create_from_video_url_keeps_accompanying_text(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    """Text pasted alongside a video link is often the ingredient list, so it must survive."""

    transcript = random_string()
    pasted_text = random_string()
    messages: list[str] = []

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        messages.append(message)
        return openai_recipe if response_schema is OpenAIRecipe else None

    def mock_download_video(url: str, temp_path: Path):
        return {
            "audio": temp_path / "mealie.mp3",
            "subtitle": None,
            "title": random_string(),
            "description": random_string(),
            "thumbnail_url": None,
            "transcription": transcript,
        }

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)
    monkeypatch.setattr(transcription_module, "download_video", mock_download_video)

    r = post_ai(api_client, unique_user, {"url": VIDEO_URL, "content": pasted_text})
    assert r.status_code == 201

    build_message = messages[0]
    assert transcript in build_message
    assert pasted_text in build_message


def test_create_from_url_combines_the_page_with_pasted_content(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    """Every source is compiled, so pasting content alongside a URL adds to the page, not replaces it."""

    page_text = random_string()
    pasted_content = random_string()
    messages: list[str] = []

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        messages.append(message)
        return openai_recipe if response_schema is OpenAIRecipe else None

    async def mock_safe_scrape_html(_: str) -> str:
        ld_json = json.dumps({"@context": "https://schema.org", "@type": "Recipe", "name": page_text})
        return f'<html><head><script type="application/ld+json">{ld_json}</script></head><body>Recipe</body></html>'

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)
    monkeypatch.setattr(compile_source_module, "safe_scrape_html", mock_safe_scrape_html)

    url = f"https://example.com/recipe/{random_string()}"
    r = post_ai(api_client, unique_user, {"url": url, "content": pasted_content})
    assert r.status_code == 201

    build_message = messages[0]
    assert page_text in build_message
    assert pasted_content in build_message

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["orgURL"] == url


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


def test_organizers_are_skipped_when_there_is_nothing_to_do(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    """With no existing organizers and creation switched off, the step can't do anything."""

    assert not any(OrganizerResolver(unique_user.repos).existing_names().values()), (
        "this test needs a group that has no organizers yet"
    )

    ai = AIResponses(recipe=openai_recipe, organizers=OpenAIOrganizers(tags=[random_string()])).install(monkeypatch)

    r = post_ai(api_client, unique_user, {"content": random_string()})
    assert r.status_code == 201
    assert "OpenAIOrganizers" not in ai.requested_schemas


def test_existing_organizers_are_attached_without_creating_new_ones(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    existing_tag = unique_user.repos.tags.create(TagSave(name=random_string(), group_id=unique_user.repos.group_id))

    new_name = random_string()
    organizers = OpenAIOrganizers(tags=[existing_tag.name, new_name], categories=[new_name], tools=[new_name])
    ai = AIResponses(recipe=openai_recipe, organizers=organizers).install(monkeypatch)

    r = post_ai(api_client, unique_user, {"content": random_string()})
    assert r.status_code == 201
    assert "OpenAIOrganizers" in ai.requested_schemas

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()

    # the existing tag is attached, and the unmatched names are dropped rather than created
    assert [tag["name"] for tag in recipe["tags"]] == [existing_tag.name]
    assert recipe["recipeCategory"] == []
    assert recipe["tools"] == []
    assert not unique_user.repos.tags.get_one(slugify(new_name), "slug")


def test_new_organizers_are_created_when_requested(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    tag_name = random_string()
    category_name = random_string()
    tool_name = random_string()

    organizers = OpenAIOrganizers(tags=[tag_name], categories=[category_name], tools=[tool_name])
    AIResponses(recipe=openai_recipe, organizers=organizers).install(monkeypatch)

    r = post_ai(api_client, unique_user, {"content": random_string(), "createNewOrganizers": "true"})
    assert r.status_code == 201

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()

    assert [tag["name"] for tag in recipe["tags"]] == [tag_name]
    assert [category["name"] for category in recipe["recipeCategory"]] == [category_name]
    assert [tool["name"] for tool in recipe["tools"]] == [tool_name]


def test_organizers_are_resolved_from_the_source_not_the_built_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    """
    Keywords live in the source, and the recipe schema has no field for them, so the organizer
    step has to read the compiled source or they're gone by the time it runs.
    """

    keyword_line = f"tags: {random_string()}, {random_string()}"
    content = f"awesome recipe\neggs, chicken, broth\nscramble the eggs\n{keyword_line}"

    messages: list[str] = []

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        messages.append(message)
        if response_schema is OpenAIRecipe:
            return openai_recipe
        if response_schema is OpenAIOrganizers:
            return OpenAIOrganizers()

        return None

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = post_ai(api_client, unique_user, {"content": content, "createNewOrganizers": "true"})
    assert r.status_code == 201

    # the last call is the organizer step; it must still be able to see the keywords
    assert keyword_line in messages[-1]


def test_existing_organizers_are_offered_to_the_provider(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    existing_tag = unique_user.repos.tags.create(TagSave(name=random_string(), group_id=unique_user.repos.group_id))

    ai = AIResponses(recipe=openai_recipe, organizers=OpenAIOrganizers()).install(monkeypatch)

    r = post_ai(api_client, unique_user, {"content": random_string()})
    assert r.status_code == 201

    organizer_prompt = ai.prompts[ai.requested_schemas.index("OpenAIOrganizers")]
    assert existing_tag.name in organizer_prompt


def test_organizer_failures_do_not_lose_the_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    recipe_name: str,
):
    """The organizer step is optional, so a failure should be logged and skipped."""

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        if response_schema is OpenAIOrganizers:
            raise Exception("organizer resolution blew up")

        return openai_recipe if response_schema is OpenAIRecipe else None

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = post_ai(api_client, unique_user, {"content": random_string(), "createNewOrganizers": "true"})
    assert r.status_code == 201

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name


def test_create_does_not_download_the_no_image_placeholder(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    """cleaner.clean stores "no image" when a recipe has none; it is not a URL."""

    AIResponses(recipe=openai_recipe).install(monkeypatch)

    async def fail_if_called(*_, **__) -> str:
        raise AssertionError("the no-image placeholder should never be fetched")

    monkeypatch.setattr(RecipeDataService, "scrape_image", fail_if_called)

    r = post_ai(api_client, unique_user, {"content": random_string()})
    assert r.status_code == 201

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["image"] != NO_IMAGE


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

    # untitled entries fall back to each schema's own default: None for ingredients, "" for steps
    assert [i["title"] for i in recipe["recipeIngredient"]] == ["For the sauce", None]
    assert [i["title"] for i in recipe["recipeInstructions"]] == ["Prep", ""]
    assert recipe["nutrition"]["calories"] == "250"
    assert recipe["nutrition"]["proteinContent"] == "12"


def test_requesting_a_translation_does_not_change_the_build_request(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
):
    """
    The build step has to ask for exactly the same thing whether or not a translation was asked for.

    Translation used to be prepended to the build message as "translate every field, including
    ingredients and instructions", which presupposes ingredients and instructions exist. That
    overrode the build prompt's rule against inventing anything, so a directive like "create a
    recipe for X" came back as a fully imagined recipe, but only with translation switched on.
    """

    content = random_string()
    messages: list[str] = []

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        if response_schema is not OpenAIRecipe:
            return None

        messages.append(message)
        # a fresh name each time, so the second import doesn't collide with the first
        return openai_recipe.model_copy(update={"name": random_string()})

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    assert post_ai(api_client, unique_user, {"content": content}).status_code == 201
    without_translation = messages[0]

    messages.clear()

    r = post_ai(api_client, unique_user, {"content": content, "translateLanguage": "French"})
    assert r.status_code == 201
    with_translation = messages[0]

    assert with_translation == without_translation
    assert "French" not in with_translation


def test_create_translates_in_its_own_step(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    recipe_name: str,
):
    """Translating is its own request, handed the recipe the build step produced."""

    translated_name = random_string()
    translated = openai_recipe.model_copy(update={"name": translated_name})
    messages: list[str] = []

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        if response_schema is not OpenAIRecipe:
            return None

        messages.append(message)
        # the build step goes first, and the translate step is handed what it built
        return translated if len(messages) > 1 else openai_recipe

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = post_ai(api_client, unique_user, {"content": random_string(), "translateLanguage": "French"})
    assert r.status_code == 201

    # the build request says nothing about translating, and the built recipe is what gets sent
    assert len(messages) == 2
    assert "French" not in messages[0]
    assert "French" in messages[1]

    # the whole recipe has to survive the trip back into the provider's schema, not just its name.
    # Anything missing here is silently dropped from the translated recipe
    translate_message = messages[1]
    assert recipe_name in translate_message
    assert openai_recipe.description in translate_message
    assert openai_recipe.ingredients[0].title in translate_message, "section titles are lost"
    for ingredient in openai_recipe.ingredients:
        assert ingredient.text in translate_message
    for instruction in openai_recipe.instructions:
        assert instruction.text in translate_message
    for note in openai_recipe.notes:
        assert note.text in translate_message

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == translated_name


def test_translation_is_skipped_when_the_source_is_already_in_the_language(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    test_image_jpg: str,
):
    compiled = OpenAICompiledSource(contains_recipe=True, content=random_string(), language="French", image_url=None)
    ai = AIResponses(recipe=openai_recipe, compiled=compiled).install(monkeypatch)

    with open(test_image_jpg, "rb") as f:
        r = post_ai(
            api_client,
            unique_user,
            data={"translateLanguage": "french"},
            files=[("images", ("recipe.jpg", f, "image/jpeg"))],
        )

    assert r.status_code == 201

    # only the build step asks for a recipe: translating French into French is a wasted call
    assert ai.requested_schemas.count("OpenAIRecipe") == 1


def test_a_failed_translation_keeps_the_untranslated_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    openai_recipe: OpenAIRecipe,
    recipe_name: str,
):
    """Translation is optional, so losing it beats losing the whole import."""

    messages: list[str] = []

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        if response_schema is not OpenAIRecipe:
            return None

        messages.append(message)
        if len(messages) > 1:
            raise Exception("the provider fell over mid-translation")

        return openai_recipe

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = post_ai(api_client, unique_user, {"content": random_string(), "translateLanguage": "French"})
    assert r.status_code == 201

    slug = json.loads(r.text)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    assert recipe["name"] == recipe_name


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


@pytest.mark.parametrize(
    ("error", "expected_key"),
    [
        (
            exceptions.OpenAIServiceError("Failed to transcribe audio: 401 invalid_api_key sk-proj-abc123"),
            "ai-request-failed",
        ),
        (
            exceptions.VideoDownloadError("Failed to download video: HTTP Error 403 at /var/lib/mealie/tmp"),
            "video-download-failed",
        ),
        (OpenAINotEnabledException("No default provider set"), "ai-not-enabled"),
        (RuntimeError("psycopg2.OperationalError: could not connect to server at 10.0.0.4"), "unknown-error"),
    ],
)
def test_provider_failures_are_reported_without_leaking_their_text(
    api_client: TestClient,
    unique_user: TestUser,
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    expected_key: str,
):
    """The AI page renders this message as-is, so it must never carry internals or a class name."""

    async def mock_get_response(self, prompt, message, *args, response_schema=None, **kwargs):
        raise error

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    r = post_ai(api_client, unique_user, {"content": random_string()})
    assert r.status_code == 400

    message = r.json()["detail"]["message"]
    assert message == translator.t(f"recipe.import-errors.{expected_key}")
    assert str(error) not in message
    assert type(error).__name__ not in message


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
