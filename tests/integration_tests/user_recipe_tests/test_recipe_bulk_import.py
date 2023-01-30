import pytest
from fastapi.testclient import TestClient

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
