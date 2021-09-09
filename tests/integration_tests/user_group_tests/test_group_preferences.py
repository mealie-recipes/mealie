from fastapi.testclient import TestClient

from mealie.schema.group.group_preferences import UpdateGroupPreferences
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/self"
    preferences = "/api/groups/preferences"


def test_get_preferences(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(Routes.preferences, headers=unique_user.token)

    assert response.status_code == 200

    preferences = response.json()

    # Spot Check Defaults
    assert preferences["recipePublic"] is True
    assert preferences["recipeShowNutrition"] is False


def test_preferences_in_group(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(Routes.base, headers=unique_user.token)

    assert response.status_code == 200

    group = response.json()

    assert group["preferences"] is not None

    # Spot Check
    assert group["preferences"]["recipePublic"] is True
    assert group["preferences"]["recipeShowNutrition"] is False


def test_update_preferences(api_client: TestClient, unique_user: TestUser) -> None:
    new_data = UpdateGroupPreferences(recipe_public=False, recipe_show_nutrition=True)

    response = api_client.put(Routes.preferences, json=new_data.dict(), headers=unique_user.token)

    assert response.status_code == 200

    preferences = response.json()

    assert preferences is not None
    assert preferences["recipePublic"] is False
    assert preferences["recipeShowNutrition"] is True

    assert_ignore_keys(new_data.dict(by_alias=True), preferences, ["id", "groupId"])
