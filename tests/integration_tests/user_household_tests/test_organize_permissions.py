"""Tests that the "User can organize group data" permission gates the
mutation endpoints for foods, tags, and categories (GHSA / issue #6883).

Read endpoints remain open; only POST/PUT/DELETE require the permission.
"""

import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

# (id, collection route, item-id route builder)
RESOURCES = [
    ("foods", api_routes.foods, api_routes.foods_item_id),
    ("tags", api_routes.organizers_tags, api_routes.organizers_tags_item_id),
    ("categories", api_routes.organizers_categories, api_routes.organizers_categories_item_id),
]
RESOURCE_IDS = [resource[0] for resource in RESOURCES]


def set_can_organize(user: TestUser, value: bool) -> None:
    db_user = user.repos.users.get_one(user.user_id)
    assert db_user
    db_user.can_organize = value
    user.repos.users.update(db_user.id, db_user)


def create_item(api_client: TestClient, user: TestUser, collection: str) -> str:
    """Creates an item as a user with the organize permission and returns its id."""
    set_can_organize(user, True)
    response = api_client.post(collection, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.parametrize("name, collection, item", RESOURCES, ids=RESOURCE_IDS)
def test_create_requires_organize_permission(
    api_client: TestClient, unique_user_fn_scoped: TestUser, name: str, collection: str, item
):
    user = unique_user_fn_scoped
    payload = {"name": random_string(10)}

    set_can_organize(user, False)
    response = api_client.post(collection, json=payload, headers=user.token)
    assert response.status_code == 403

    set_can_organize(user, True)
    response = api_client.post(collection, json=payload, headers=user.token)
    assert response.status_code == 201


@pytest.mark.parametrize("name, collection, item", RESOURCES, ids=RESOURCE_IDS)
def test_update_requires_organize_permission(
    api_client: TestClient, unique_user_fn_scoped: TestUser, name: str, collection: str, item
):
    user = unique_user_fn_scoped
    item_id = create_item(api_client, user, collection)
    payload = {"id": item_id, "name": random_string(10)}

    set_can_organize(user, False)
    response = api_client.put(item(item_id), json=payload, headers=user.token)
    assert response.status_code == 403

    set_can_organize(user, True)
    response = api_client.put(item(item_id), json=payload, headers=user.token)
    assert response.status_code == 200


@pytest.mark.parametrize("name, collection, item", RESOURCES, ids=RESOURCE_IDS)
def test_delete_requires_organize_permission(
    api_client: TestClient, unique_user_fn_scoped: TestUser, name: str, collection: str, item
):
    user = unique_user_fn_scoped
    item_id = create_item(api_client, user, collection)

    set_can_organize(user, False)
    response = api_client.delete(item(item_id), headers=user.token)
    assert response.status_code == 403

    set_can_organize(user, True)
    response = api_client.delete(item(item_id), headers=user.token)
    assert response.status_code == 200


def test_food_merge_requires_organize_permission(api_client: TestClient, unique_user_fn_scoped: TestUser):
    user = unique_user_fn_scoped
    from_food = create_item(api_client, user, api_routes.foods)
    to_food = create_item(api_client, user, api_routes.foods)
    payload = {"fromFood": from_food, "toFood": to_food}

    set_can_organize(user, False)
    response = api_client.put(api_routes.foods_merge, json=payload, headers=user.token)
    assert response.status_code == 403

    set_can_organize(user, True)
    response = api_client.put(api_routes.foods_merge, json=payload, headers=user.token)
    assert response.status_code == 200


def test_tool_update_on_hand_does_not_require_organize_permission(
    api_client: TestClient, unique_user_fn_scoped: TestUser
):
    """Marking a tool as on hand only changes which households have it, which is
    household data, not group organization (issue #9270)."""
    user = unique_user_fn_scoped
    tool_id = create_item(api_client, user, api_routes.organizers_tools)
    tool = api_client.get(api_routes.organizers_tools_item_id(tool_id), headers=user.token).json()
    household = user.repos.households.get_one(user.household_id)
    assert household

    set_can_organize(user, False)

    payload = {"name": tool["name"], "householdsWithTool": [household.slug]}
    response = api_client.put(api_routes.organizers_tools_item_id(tool_id), json=payload, headers=user.token)
    assert response.status_code == 200
    assert response.json()["householdsWithTool"] == [household.slug]

    payload = {"name": tool["name"], "householdsWithTool": []}
    response = api_client.put(api_routes.organizers_tools_item_id(tool_id), json=payload, headers=user.token)
    assert response.status_code == 200
    assert response.json()["householdsWithTool"] == []


def test_tool_rename_requires_organize_permission(api_client: TestClient, unique_user_fn_scoped: TestUser):
    user = unique_user_fn_scoped
    tool_id = create_item(api_client, user, api_routes.organizers_tools)
    tool = api_client.get(api_routes.organizers_tools_item_id(tool_id), headers=user.token).json()

    payload = {"name": random_string(10), "householdsWithTool": tool["householdsWithTool"]}

    set_can_organize(user, False)
    response = api_client.put(api_routes.organizers_tools_item_id(tool_id), json=payload, headers=user.token)
    assert response.status_code == 403

    set_can_organize(user, True)
    response = api_client.put(api_routes.organizers_tools_item_id(tool_id), json=payload, headers=user.token)
    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]


@pytest.mark.parametrize("name, collection, item", RESOURCES, ids=RESOURCE_IDS)
def test_read_endpoints_do_not_require_organize_permission(
    api_client: TestClient, unique_user_fn_scoped: TestUser, name: str, collection: str, item
):
    user = unique_user_fn_scoped
    item_id = create_item(api_client, user, collection)

    set_can_organize(user, False)

    response = api_client.get(collection, headers=user.token)
    assert response.status_code == 200

    response = api_client.get(item(item_id), headers=user.token)
    assert response.status_code == 200
