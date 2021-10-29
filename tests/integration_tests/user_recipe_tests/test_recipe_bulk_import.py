import pytest
from fastapi.testclient import TestClient

from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/recipes"
    bulk = "/api/recipes/create-url/bulk"

    def item(item_id: str) -> str:
        return f"{Routes.base}/{item_id}"


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

    response = api_client.post(Routes.bulk, json=recipes, headers=unique_user.token)

    assert response.status_code == 201

    for slug in slugs:
        response = api_client.get(Routes.item(slug), headers=unique_user.token)
        assert response.status_code == 200
