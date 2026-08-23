from fastapi.testclient import TestClient

from mealie.schema.household.household_preferences import UpdateHouseholdPreferences
from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.factories import random_bool
from tests.utils.fixture_schemas import TestUser


def test_get_preferences(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(api_routes.households_preferences, headers=unique_user.token)
    assert response.status_code == 200

    preferences = response.json()

    assert preferences["recipePublic"] in {True, False}
    assert preferences["recipeShowNutrition"] in {True, False}


def test_preferences_in_household(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(api_routes.households_self, headers=unique_user.token)

    assert response.status_code == 200

    household = response.json()

    assert household["preferences"] is not None

    # Spot Check
    assert household["preferences"]["recipePublic"] in {True, False}
    assert household["preferences"]["recipeShowNutrition"] in {True, False}


def test_update_preferences_no_permission(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    unique_user, other_user = user_tuple

    user = other_user.repos.users.get_one(unique_user.user_id)
    assert user
    user.can_manage_household = False
    other_user.repos.users.update(user.id, user)

    new_data = UpdateHouseholdPreferences(recipe_public=random_bool(), recipe_show_nutrition=random_bool())
    response = api_client.put(api_routes.households_preferences, json=new_data.model_dump(), headers=unique_user.token)
    assert response.status_code == 403


def test_update_preferences(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    unique_user, other_user = user_tuple

    user = other_user.repos.users.get_one(unique_user.user_id)
    assert user
    user.can_manage_household = True
    other_user.repos.users.update(user.id, user)

    new_data = UpdateHouseholdPreferences(recipe_public=random_bool(), recipe_show_nutrition=random_bool())
    response = api_client.put(api_routes.households_preferences, json=new_data.model_dump(), headers=unique_user.token)
    assert response.status_code == 200

    preferences = response.json()
    assert preferences is not None
    assert preferences["recipePublic"] == new_data.recipe_public
    assert preferences["recipeShowNutrition"] == new_data.recipe_show_nutrition
    assert_ignore_keys(new_data.model_dump(by_alias=True), preferences, ["id", "householdId"])


def test_display_preference_defaults(api_client: TestClient, unique_user: TestUser) -> None:
    """Households start out showing recipes as written, so nothing changes for existing installs."""
    response = api_client.get(api_routes.households_preferences, headers=unique_user.token)
    assert response.status_code == 200

    preferences = response.json()
    assert preferences["defaultUnitSystem"] == "original"
    assert preferences["defaultTemperatureUnit"] == "system"


def test_update_display_preferences(api_client: TestClient, unique_user: TestUser) -> None:
    new_data = UpdateHouseholdPreferences(default_unit_system="metric", default_temperature_unit="fahrenheit")
    response = api_client.put(api_routes.households_preferences, json=new_data.model_dump(), headers=unique_user.token)
    assert response.status_code == 200

    preferences = api_client.get(api_routes.households_preferences, headers=unique_user.token).json()
    assert preferences["defaultUnitSystem"] == "metric"
    assert preferences["defaultTemperatureUnit"] == "fahrenheit"


def test_display_preferences_reject_unknown_values(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.put(
        api_routes.households_preferences,
        json={"defaultUnitSystem": "klingon"},
        headers=unique_user.token,
    )
    assert response.status_code == 422
