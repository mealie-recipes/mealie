import pytest
from fastapi.testclient import TestClient

from mealie.pkgs import safehttp
from mealie.routes.recipe.recipe_crud_routes import ASSET_MAX_DOWNLOAD_BYTES
from mealie.schema.recipe.recipe import Recipe
from mealie.services.recipe.recipe_data_service import (
    InvalidDomainError,
    NotAnImageError,
    RecipeDataService,
)
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser

IMAGE_BYTES = b"pretend-png-bytes"


def _patch_download(monkeypatch, result=None, *, raises: Exception | None = None) -> dict:
    """Replaces the server-side download, capturing the url and budget it was given."""
    captured: dict = {}

    async def fake_fetch_image(self, image_url, max_bytes=None):
        captured["url"] = image_url
        captured["max_bytes"] = max_bytes
        if raises is not None:
            raise raises
        return result

    monkeypatch.setattr(RecipeDataService, "fetch_image", fake_fetch_image)
    return captured


def test_create_asset_from_url(
    api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe, monkeypatch
):
    recipe = recipe_ingredient_only
    captured = _patch_download(monkeypatch, (IMAGE_BYTES, "png"))

    response = api_client.post(
        api_routes.recipes_slug_assets_url(recipe.slug),
        json={"url": "https://example.test/photos/pancakes.png?v=2"},
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert captured["url"] == "https://example.test/photos/pancakes.png?v=2"

    # The name comes from the URL's filename, ignoring the query string.
    asset = response.json()
    assert asset["name"] == "pancakes"
    assert asset["fileName"] == "pancakes.png"

    stored = recipe.asset_dir / asset["fileName"]
    assert stored.exists()
    assert stored.read_bytes() == IMAGE_BYTES

    recipe_response = api_client.get(api_routes.recipes_slug(recipe.slug), headers=unique_user.token).json()
    assert recipe_response["assets"][0]["fileName"] == "pancakes.png"


def test_create_asset_from_url_applies_the_download_budget(
    api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe, monkeypatch
):
    """The bytes are stored as-is, so the download must be capped rather than bounded by time."""
    captured = _patch_download(monkeypatch, (IMAGE_BYTES, "png"))

    response = api_client.post(
        api_routes.recipes_slug_assets_url(recipe_ingredient_only.slug),
        json={"url": "https://example.test/pancakes.png"},
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert captured["max_bytes"] == ASSET_MAX_DOWNLOAD_BYTES


@pytest.mark.parametrize(
    ("url", "expected_name"),
    [
        ("https://example.test/pancakes.png", "pancakes"),
        ("https://example.test/download?id=123", "download"),  # extensionless is still a name
        ("https://example.test/", "image"),  # no filename at all
        ("https://example.test/$.png", "image"),  # a filename that slugifies to nothing
    ],
)
def test_create_asset_from_url_names_the_asset_after_the_file(
    api_client: TestClient,
    unique_user: TestUser,
    recipe_ingredient_only: Recipe,
    monkeypatch,
    url: str,
    expected_name: str,
):
    _patch_download(monkeypatch, (IMAGE_BYTES, "png"))

    response = api_client.post(
        api_routes.recipes_slug_assets_url(recipe_ingredient_only.slug),
        json={"url": url},
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert response.json()["name"] == expected_name


def test_create_asset_from_url_rejects_scriptable_image_types(
    api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe, monkeypatch
):
    """SVG is an image the browser will execute, so it must not become an asset (GHSA-gfwc-pjx4-mg9p)."""
    recipe = recipe_ingredient_only
    _patch_download(monkeypatch, (b"<svg onload=alert(1)/>", "svg+xml"))

    response = api_client.post(
        api_routes.recipes_slug_assets_url(recipe.slug),
        json={"url": "https://example.test/evil.svg"},
        headers=unique_user.token,
    )

    assert response.status_code == 400
    assert not any(recipe.asset_dir.iterdir())


@pytest.mark.parametrize(
    "raises",
    [
        NotAnImageError("not an image"),
        InvalidDomainError("blocked"),
        safehttp.ResponseTooLargeError("too big"),
    ],
)
def test_create_asset_from_url_reports_download_failures(
    api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe, monkeypatch, raises: Exception
):
    recipe = recipe_ingredient_only
    _patch_download(monkeypatch, raises=raises)

    response = api_client.post(
        api_routes.recipes_slug_assets_url(recipe.slug),
        json={"url": "https://example.test/pancakes.png"},
        headers=unique_user.token,
    )

    assert response.status_code == 400
    assert not any(recipe.asset_dir.iterdir())


def test_create_asset_from_url_when_nothing_downloads(
    api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe, monkeypatch
):
    recipe = recipe_ingredient_only
    _patch_download(monkeypatch, None)

    response = api_client.post(
        api_routes.recipes_slug_assets_url(recipe.slug),
        json={"url": "https://example.test/pancakes.png"},
        headers=unique_user.token,
    )

    assert response.status_code == 400
    assert not any(recipe.asset_dir.iterdir())


def test_create_asset_from_url_requires_authentication(
    api_client: TestClient, recipe_ingredient_only: Recipe, monkeypatch
):
    """The server fetches whatever url it is handed, so this must never be reachable anonymously."""
    _patch_download(monkeypatch, (IMAGE_BYTES, "png"))

    response = api_client.post(
        api_routes.recipes_slug_assets_url(recipe_ingredient_only.slug),
        json={"url": "https://example.test/pancakes.png"},
    )

    assert response.status_code == 401
