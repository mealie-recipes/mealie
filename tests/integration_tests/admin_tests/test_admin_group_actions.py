from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.factories import random_bool, random_string
from tests.utils.fixture_schemas import TestUser


def test_home_group_not_deletable(api_client: TestClient, admin_user: TestUser):
    response = api_client.delete(api_routes.admin_groups_item_id(admin_user.group_id), headers=admin_user.token)
    assert response.status_code == 400


def test_admin_group_routes_are_restricted(api_client: TestClient, unique_user: TestUser, admin_user: TestUser):
    response = api_client.get(api_routes.admin_groups, headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.post(api_routes.admin_groups, json={}, headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.get(api_routes.admin_groups_item_id(admin_user.group_id), headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.get(api_routes.admin_users_item_id(admin_user.group_id), headers=unique_user.token)
    assert response.status_code == 403


def test_admin_create_group(api_client: TestClient, admin_user: TestUser):
    response = api_client.post(api_routes.admin_groups, json={"name": random_string()}, headers=admin_user.token)
    assert response.status_code == 201


def test_admin_update_group(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    update_payload = {
        "id": unique_user.group_id,
        "name": "New Name",
        "preferences": {"privateGroup": random_bool()},
    }

    response = api_client.put(
        api_routes.admin_groups_item_id(unique_user.group_id),
        json=update_payload,
        headers=admin_user.token,
    )

    assert response.status_code == 200

    as_json = response.json()

    assert as_json["name"] == update_payload["name"]
    assert_ignore_keys(as_json["preferences"], update_payload["preferences"])  # type: ignore


def test_admin_delete_group(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    # Delete User
    response = api_client.delete(api_routes.admin_users_item_id(unique_user.user_id), headers=admin_user.token)
    assert response.status_code == 200

    # Delete Household
    response = api_client.delete(
        api_routes.admin_households_item_id(unique_user.household_id), headers=admin_user.token
    )
    assert response.status_code == 200

    # Ensure Household is Deleted
    response = api_client.get(api_routes.admin_households_item_id(unique_user.household_id), headers=admin_user.token)
    assert response.status_code == 404

    # Delete Group
    response = api_client.delete(api_routes.admin_groups_item_id(unique_user.group_id), headers=admin_user.token)
    assert response.status_code == 200

    # Ensure Group is Deleted
    response = api_client.get(api_routes.admin_groups_item_id(unique_user.group_id), headers=admin_user.token)
    assert response.status_code == 404
