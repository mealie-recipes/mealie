import json

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from mealie.lang.providers import Translator
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import RecipeDraft
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.scraper import recipe_bulk_scraper
from mealie.services.scraper.scraped_extras import ScrapedExtras
from mealie.services.scraper.scraper_strategies import RecipeScraperPackage
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


@pytest.mark.skip("Long Running Scraper")
def test_bulk_import(api_client: TestClient, unique_user: TestUser):
    recipes = {
        "imports": [
            {"url": "https://www.bonappetit.com/recipe/caramel-crunch-chocolate-chunklet-cookies"},
            {"url": "https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/"},
        ]
    }

    slugs = [
        "caramel-crunch-chocolate-chunklet-cookies",
        "best-chocolate-chip-cookies",
    ]

    response = api_client.post(api_routes.recipes_create_url_bulk, json=recipes, headers=unique_user.token)

    assert response.status_code == 202

    for slug in slugs:
        response = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
        assert response.status_code == 200


def test_bulk_import_persists_tools(api_client: TestClient, unique_user: TestUser, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(RecipeDataService, "scrape_image", lambda *_: "TEST_IMAGE")
    html = RecipeScraperPackage.ld_json_to_html(
        json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "Recipe",
                "name": "Bulk equipment regression",
                "recipeIngredient": ["1 apple"],
                "recipeInstructions": ["Slice the apple."],
                "tool": ["Equipment 1"],
            }
        )
    )
    create_from_html = recipe_bulk_scraper.create_from_html

    async def scrape(
        url: str, repos: AllRepositories, translator: Translator
    ) -> tuple[RecipeDraft, ScrapedExtras | None]:
        return await create_from_html(url, repos, translator, html)

    monkeypatch.setattr(recipe_bulk_scraper, "create_from_html", scrape)
    response = api_client.post(
        api_routes.recipes_create_url_bulk,
        json={"imports": [{"url": "https://example.com/recipe"}]},
        headers=unique_user.token,
    )
    assert response.status_code == 202
    recipe = api_client.get(api_routes.recipes_slug("bulk-equipment-regression"), headers=unique_user.token)
    assert recipe.status_code == 200
    assert [tool["name"] for tool in recipe.json()["tools"]] == ["Equipment 1"]
