from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.factories import random_bool, random_string
from tests.utils.fixture_schemas import TestUser


def test_home_household_not_deletable(api_client: TestClient, admin_user: TestUser):
    response = api_client.delete(api_routes.admin_households_item_id(admin_user.household_id), headers=admin_user.token)
    assert response.status_code == 400


def test_admin_household_routes_are_restricted(api_client: TestClient, unique_user: TestUser, admin_user: TestUser):
    response = api_client.get(api_routes.admin_households, headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.post(api_routes.admin_households, json={}, headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.get(api_routes.admin_households_item_id(admin_user.household_id), headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.get(api_routes.admin_households_item_id(admin_user.household_id), headers=unique_user.token)
    assert response.status_code == 403


def test_admin_create_household(api_client: TestClient, admin_user: TestUser):
    response = api_client.post(
        api_routes.admin_households,
        json={"name": random_string(), "groupId": admin_user.group_id},
        headers=admin_user.token,
    )
    assert response.status_code == 201


def test_admin_update_household(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    update_payload = {
        "id": unique_user.household_id,
        "groupId": admin_user.group_id,
        "name": "New Name",
        "preferences": {
            "privateHousehold": random_bool(),
            "lockRecipeEditsFromOtherHouseholds": random_bool(),
            "firstDayOfWeek": 2,
            "recipePublic": random_bool(),
            "recipeShowNutrition": random_bool(),
            "recipeShowAssets": random_bool(),
            "recipeLandscapeView": random_bool(),
            "recipeDisableComments": random_bool(),
            "recipeDisableAmount": random_bool(),
        },
    }

    response = api_client.put(
        api_routes.admin_households_item_id(unique_user.household_id),
        json=update_payload,
        headers=admin_user.token,
    )

    assert response.status_code == 200

    as_json = response.json()

    assert as_json["name"] == update_payload["name"]
    assert_ignore_keys(as_json["preferences"], update_payload["preferences"])  # type: ignore


def test_admin_delete_household(unfiltered_database: AllRepositories, api_client: TestClient, admin_user: TestUser):
    group = unfiltered_database.groups.create({"name": random_string()})
    household = unfiltered_database.households.create({"name": random_string(), "group_id": group.id})
    response = api_client.delete(api_routes.admin_households_item_id(household.id), headers=admin_user.token)
    assert response.status_code == 200

    response = api_client.get(api_routes.admin_households_item_id(household.id), headers=admin_user.token)
    assert response.status_code == 404
