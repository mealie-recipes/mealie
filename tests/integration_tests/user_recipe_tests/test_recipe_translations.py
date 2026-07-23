import pytest
from fastapi.testclient import TestClient

from mealie.schema.group.ai_providers import AIProviderCreate, AIProviderSettingsUpdate
from mealie.schema.openai.recipe_translation import OpenAITranslatedRecipe, OpenAITranslatedString
from mealie.services.openai import OpenAIService
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

TARGET_LOCALE = "es-ES"


@pytest.fixture
def ai_enabled(unique_user: TestUser):
    provider = unique_user.repos.group_ai_providers.create(
        AIProviderCreate(name=random_string(), model="gpt-4o", api_key="test-key")
    )
    unique_user.repos.group_ai_provider_settings.update(
        unique_user.repos.group_id,
        AIProviderSettingsUpdate(default_provider_id=provider.id, audio_provider_id=None, image_provider_id=None),
    )


def _create_recipe(api_client: TestClient, user: TestUser) -> dict:
    r = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=user.token)
    assert r.status_code == 201
    slug = r.json()

    recipe_url = api_routes.recipes_slug(slug)
    recipe = api_client.get(recipe_url, headers=user.token).json()
    recipe["description"] = "A tasty dish"
    recipe["recipeInstructions"] = [{"text": "Boil the water."}, {"text": "Add the pasta."}]
    recipe["recipeIngredient"] = [
        {"note": "200g pasta", "quantity": 200, "unit": None, "food": None},
        {"note": "1 pinch salt", "quantity": 1, "unit": None, "food": None},
    ]
    assert api_client.put(recipe_url, json=recipe, headers=user.token).status_code == 200
    return api_client.get(recipe_url, headers=user.token).json()


def _mock_translation(monkeypatch: pytest.MonkeyPatch, recipe: dict):
    """Patch the AI call to echo back a deterministic 'translation' keyed to the recipe's stable ids."""

    step_keys = [str(s["id"]) for s in recipe["recipeInstructions"]]
    ingredient_keys = [str(i["referenceId"]) for i in recipe["recipeIngredient"]]

    async def mock_get_response(self, prompt: str, message: str, *args, **kwargs) -> OpenAITranslatedRecipe:
        return OpenAITranslatedRecipe(
            name="Nombre traducido",
            description="Un plato sabroso",
            recipe_yield=None,
            instructions=[OpenAITranslatedString(key=k, value=f"ES paso {k}") for k in step_keys],
            ingredients=[OpenAITranslatedString(key=k, value=f"ES ingrediente {k}") for k in ingredient_keys],
        )

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)


def test_translate_and_read_back(
    api_client: TestClient, monkeypatch: pytest.MonkeyPatch, unique_user: TestUser, ai_enabled
):
    recipe = _create_recipe(api_client, unique_user)
    _mock_translation(monkeypatch, recipe)
    slug = recipe["slug"]

    r = api_client.post(
        api_routes.recipes_slug_translations(slug), json={"locale": TARGET_LOCALE}, headers=unique_user.token
    )
    assert r.status_code == 201
    assert r.json()["locale"] == TARGET_LOCALE
    assert r.json()["isStale"] is False

    # Reading with the locale returns translated text
    translated = api_client.get(
        api_routes.recipes_slug(slug), params={"locale": TARGET_LOCALE}, headers=unique_user.token
    ).json()
    assert translated["name"] == "Nombre traducido"
    assert translated["description"] == "Un plato sabroso"
    assert all(step["text"].startswith("ES paso") for step in translated["recipeInstructions"])
    assert translated["translatedLocale"] == TARGET_LOCALE
    assert {t["locale"] for t in translated["availableTranslations"]} == {TARGET_LOCALE}

    # Ingredient structure is untouched — only the note text changed
    original = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    for orig, trans in zip(original["recipeIngredient"], translated["recipeIngredient"], strict=True):
        assert orig["quantity"] == trans["quantity"]
        assert orig["referenceId"] == trans["referenceId"]
        assert trans["note"].startswith("ES ingrediente")
        assert not orig["note"].startswith("ES ingrediente")


def test_unknown_locale_falls_back_to_original(
    api_client: TestClient, monkeypatch: pytest.MonkeyPatch, unique_user: TestUser, ai_enabled
):
    recipe = _create_recipe(api_client, unique_user)
    _mock_translation(monkeypatch, recipe)
    slug = recipe["slug"]
    api_client.post(
        api_routes.recipes_slug_translations(slug), json={"locale": TARGET_LOCALE}, headers=unique_user.token
    )

    # A locale with no stored translation returns the canonical recipe
    r = api_client.get(api_routes.recipes_slug(slug), params={"locale": "fr-FR"}, headers=unique_user.token).json()
    assert r["name"] == recipe["name"]
    assert r["translatedLocale"] is None

    # "original" is explicit passthrough
    r = api_client.get(api_routes.recipes_slug(slug), params={"locale": "original"}, headers=unique_user.token).json()
    assert r["name"] == recipe["name"]


def test_editing_recipe_marks_translation_stale(
    api_client: TestClient, monkeypatch: pytest.MonkeyPatch, unique_user: TestUser, ai_enabled
):
    recipe = _create_recipe(api_client, unique_user)
    _mock_translation(monkeypatch, recipe)
    slug = recipe["slug"]
    recipe_url = api_routes.recipes_slug(slug)

    api_client.post(
        api_routes.recipes_slug_translations(slug), json={"locale": TARGET_LOCALE}, headers=unique_user.token
    )

    # Edit the source text (description only, so the slug is unchanged)
    recipe["description"] = "A brand new description"
    put = api_client.put(recipe_url, json=recipe, headers=unique_user.token)
    assert put.status_code == 200

    # Translation still exists, but is now flagged stale
    translations = api_client.get(api_routes.recipes_slug_translations(slug), headers=unique_user.token).json()
    assert len(translations) == 1
    assert translations[0]["locale"] == TARGET_LOCALE
    assert translations[0]["isStale"] is True


def test_delete_translation(
    api_client: TestClient, monkeypatch: pytest.MonkeyPatch, unique_user: TestUser, ai_enabled
):
    recipe = _create_recipe(api_client, unique_user)
    _mock_translation(monkeypatch, recipe)
    slug = recipe["slug"]

    api_client.post(
        api_routes.recipes_slug_translations(slug), json={"locale": TARGET_LOCALE}, headers=unique_user.token
    )
    r = api_client.delete(
        api_routes.recipes_slug_translations_locale(slug, TARGET_LOCALE), headers=unique_user.token
    )
    assert r.status_code == 200

    translations = api_client.get(api_routes.recipes_slug_translations(slug), headers=unique_user.token).json()
    assert translations == []


def test_translation_requires_ai(api_client: TestClient, unique_user_fn_scoped: TestUser):
    """No AI provider configured -> 400. Uses a function-scoped user so no AI provider leaks in."""
    recipe = _create_recipe(api_client, unique_user_fn_scoped)
    r = api_client.post(
        api_routes.recipes_slug_translations(recipe["slug"]),
        json={"locale": TARGET_LOCALE},
        headers=unique_user_fn_scoped.token,
    )
    assert r.status_code == 400
