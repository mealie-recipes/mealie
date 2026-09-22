from fastapi.testclient import TestClient

from mealie.schema.household.household import HouseholdRecipeSummary
from mealie.schema.recipe.recipe import Recipe, RecipeSummary


def test_openapi_returns_json(api_client: TestClient):
    response = api_client.get("openapi.json")
    assert response.status_code == 200


def test_last_made_is_only_exposed_on_household_recipes():
    assert "last_made" not in Recipe.model_fields
    assert "last_made" not in RecipeSummary.model_fields
    assert "last_made" in HouseholdRecipeSummary.model_fields


def test_last_made_update_route_remains_available(api_client: TestClient):
    response = api_client.get("openapi.json")
    assert "/api/recipes/{slug}/last-made" in response.json()["paths"]
