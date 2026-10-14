"""Tests that the "User can organize group data" permission gates the
mutation endpoints for foods, tags, categories, units, tools, and labels
(GHSA / issue #6883, issue #8712).

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
    ("units", api_routes.units, api_routes.units_item_id),
    ("tools", api_routes.organizers_tools, api_routes.organizers_tools_item_id),
    ("labels", api_routes.groups_labels, api_routes.groups_labels_item_id),
]
RESOURCE_IDS = [resource[0] for resource in RESOURCES]
COLLECTIONS = {resource[0]: resource[1] for resource in RESOURCES}

# (id, merge route, merge HTTP method, merge payload builder)
MERGE_RESOURCES = [
    ("foods", api_routes.foods_merge, "put", lambda from_id, to_id: {"fromFood": from_id, "toFood": to_id}),
    ("units", api_routes.units_merge, "put", lambda from_id, to_id: {"fromUnit": from_id, "toUnit": to_id}),
    (
        "tools",
        api_routes.organizers_tools_merge,
        "post",
        lambda from_id, to_id: {"fromId": from_id, "toId": to_id},
    ),
    (
        "labels",
        api_routes.groups_labels_merge,
        "post",
        lambda from_id, to_id: {"fromId": from_id, "toId": to_id},
    ),
]
MERGE_RESOURCE_IDS = [resource[0] for resource in MERGE_RESOURCES]


def set_can_organize(user: TestUser, value: bool) -> None:
    db_user = user.repos.users.get_one(user.user_id)
    assert db_user
    db_user.can_organize = value
    user.repos.users.update(db_user.id, db_user)


def create_item(api_client: TestClient, user: TestUser, collection: str) -> str:
    """Creates an item as a user with the organize permission and returns its id."""
    set_can_organize(user, True)
    response = api_client.post(collection, json={"name": random_string(10)}, headers=user.token)
    # labels POST returns 200; all other resources return 201
    assert response.status_code in (200, 201)
    return response.json()["id"]


def update_payload(user: TestUser, name: str, item_id: str) -> dict:
    payload: dict = {"id": item_id, "name": random_string(10)}
    if name == "labels":
        # MultiPurposeLabelUpdate requires the group id in the request body
        payload["groupId"] = user.group_id
    return payload


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
    # labels POST returns 200; all other resources return 201
    assert response.status_code in (200, 201)


@pytest.mark.parametrize("name, collection, item", RESOURCES, ids=RESOURCE_IDS)
def test_update_requires_organize_permission(
    api_client: TestClient, unique_user_fn_scoped: TestUser, name: str, collection: str, item
):
    user = unique_user_fn_scoped
    item_id = create_item(api_client, user, collection)
    payload = update_payload(user, name, item_id)

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


@pytest.mark.parametrize("name, merge_route, method, payload", MERGE_RESOURCES, ids=MERGE_RESOURCE_IDS)
def test_merge_requires_organize_permission(
    api_client: TestClient, unique_user_fn_scoped: TestUser, name: str, merge_route: str, method: str, payload
):
    user = unique_user_fn_scoped
    collection = COLLECTIONS[name]
    from_id = create_item(api_client, user, collection)
    to_id = create_item(api_client, user, collection)
    body = payload(from_id, to_id)

    set_can_organize(user, False)
    response = api_client.request(method, merge_route, json=body, headers=user.token)
    assert response.status_code == 403

    set_can_organize(user, True)
    response = api_client.request(method, merge_route, json=body, headers=user.token)
    assert response.status_code == 200


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
