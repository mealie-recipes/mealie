from fastapi.testclient import TestClient

from tests.utils.fixture_schemas import TestUser


class Routes:
    permissions = "/api/groups/permissions"


def test_get_preferences(api_client: TestClient, unique_user: TestUser) -> None:

    response = api_client.get(Routes.permissions, headers=unique_user.token)

    assert response.status_code == 200

    preferences = response.json()

    # Spot Check Defaults
    assert preferences["recipePublic"] is True
    assert preferences["recipeShowNutrition"] is False
