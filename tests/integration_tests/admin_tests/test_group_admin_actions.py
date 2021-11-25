from fastapi.testclient import TestClient

from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.factories import random_bool, random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/admin/groups"

    def item(id: str) -> str:
        return f"{Routes.base}/{id}"

    def user(id: str) -> str:
        return f"api/admin/users/{id}"


def test_home_group_not_deletable(api_client: TestClient, admin_user: TestUser):
    response = api_client.delete(Routes.item(1), headers=admin_user.token)
    assert response.status_code == 400


def test_admin_group_routes_are_restricted(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(Routes.base, headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.post(Routes.base, json={}, headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.get(Routes.item(1), headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.get(Routes.user(1), headers=unique_user.token)
    assert response.status_code == 403


def test_admin_create_group(api_client: TestClient, admin_user: TestUser):
    response = api_client.post(Routes.base, json={"name": random_string()}, headers=admin_user.token)
    assert response.status_code == 201


def test_admin_update_group(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    update_payload = {
        "id": unique_user.group_id,
        "name": "New Name",
        "preferences": {
            "privateGroup": random_bool(),
            "firstDayOfWeek": 2,
            "recipePublic": random_bool(),
            "recipeShowNutrition": random_bool(),
            "recipeShowAssets": random_bool(),
            "recipeLandscapeView": random_bool(),
            "recipeDisableComments": random_bool(),
            "recipeDisableAmount": random_bool(),
        },
    }

    response = api_client.put(Routes.item(unique_user.group_id), json=update_payload, headers=admin_user.token)

    assert response.status_code == 200

    as_json = response.json()

    assert as_json["name"] == update_payload["name"]
    assert_ignore_keys(as_json["preferences"], update_payload["preferences"])


def test_admin_delete_group(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    # Delete User
    response = api_client.delete(Routes.user(unique_user.user_id), headers=admin_user.token)
    assert response.status_code == 200

    # Delete Group
    response = api_client.delete(Routes.item(unique_user.group_id), headers=admin_user.token)
    assert response.status_code == 200

    # Ensure Group is Deleted
    response = api_client.get(Routes.item(unique_user.user_id), headers=admin_user.token)
    assert response.status_code == 404
