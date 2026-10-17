"""Tests that the "User can organize group data" permission gates the
mutation endpoints for foods, units, tags, categories, tools, and labels.

Read endpoints remain open; only POST/PUT/DELETE require the permission.
"""

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

# (id, collection route, item-id route builder, create status)
RESOURCES = [
    ("foods", api_routes.foods, api_routes.foods_item_id, 201),
    ("units", api_routes.units, api_routes.units_item_id, 201),
    ("tags", api_routes.organizers_tags, api_routes.organizers_tags_item_id, 201),
    ("categories", api_routes.organizers_categories, api_routes.organizers_categories_item_id, 201),
    ("tools", api_routes.organizers_tools, api_routes.organizers_tools_item_id, 201),
    ("labels", api_routes.groups_labels, api_routes.groups_labels_item_id, 200),
]
RESOURCE_IDS = [resource[0] for resource in RESOURCES]

# (id, collection route, create status, HTTP method, merge route, payload keys)
MERGES = [
    ("foods", api_routes.foods, 201, "put", api_routes.foods_merge, ("fromFood", "toFood")),
    ("units", api_routes.units, 201, "put", api_routes.units_merge, ("fromUnit", "toUnit")),
    ("tags", api_routes.organizers_tags, 201, "post", api_routes.organizers_tags_merge, ("fromId", "toId")),
    (
        "categories",
        api_routes.organizers_categories,
        201,
        "post",
        api_routes.organizers_categories_merge,
        ("fromId", "toId"),
    ),
    ("tools", api_routes.organizers_tools, 201, "post", api_routes.organizers_tools_merge, ("fromId", "toId")),
    ("labels", api_routes.groups_labels, 200, "post", api_routes.groups_labels_merge, ("fromId", "toId")),
]


def set_can_organize(user: TestUser, value: bool) -> None:
    db_user = user.repos.users.get_one(user.user_id)
    assert db_user
    db_user.can_organize = value
    user.repos.users.update(db_user.id, db_user)


def collection_items(api_client: TestClient, user: TestUser, collection: str) -> dict[str, dict]:
    response = api_client.get(collection, params={"perPage": -1}, headers=user.token)
    assert response.status_code == 200
    return {item["id"]: item for item in response.json()["items"]}


def create_item(api_client: TestClient, user: TestUser, collection: str, create_status: int) -> str:
    """Creates an item as a user with the organize permission and returns its id."""
    set_can_organize(user, True)
    response = api_client.post(collection, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == create_status
    return response.json()["id"]


@pytest.mark.parametrize("name, collection, item, create_status", RESOURCES, ids=RESOURCE_IDS)
def test_create_requires_organize_permission(
    api_client: TestClient,
    unique_user_fn_scoped: TestUser,
    name: str,
    collection: str,
    item: Callable[[str], str],
    create_status: int,
) -> None:
    user = unique_user_fn_scoped
    payload = {"name": random_string(10)}

    set_can_organize(user, False)
    before = collection_items(api_client, user, collection)
    response = api_client.post(collection, json=payload, headers=user.token)
    assert response.status_code == 403
    assert collection_items(api_client, user, collection) == before

    set_can_organize(user, True)
    response = api_client.post(collection, json=payload, headers=user.token)
    assert response.status_code == create_status
    assert response.json()["name"] == payload["name"]


@pytest.mark.parametrize("name, collection, item, create_status", RESOURCES, ids=RESOURCE_IDS)
def test_update_requires_organize_permission(
    api_client: TestClient,
    unique_user_fn_scoped: TestUser,
    name: str,
    collection: str,
    item: Callable[[str], str],
    create_status: int,
) -> None:
    user = unique_user_fn_scoped
    item_id = create_item(api_client, user, collection, create_status)
    payload = {"id": item_id, "groupId": user.group_id, "name": random_string(10)}

    set_can_organize(user, False)
    before = collection_items(api_client, user, collection)
    response = api_client.put(item(item_id), json=payload, headers=user.token)
    assert response.status_code == 403
    assert collection_items(api_client, user, collection) == before

    set_can_organize(user, True)
    response = api_client.put(item(item_id), json=payload, headers=user.token)
    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]
    assert collection_items(api_client, user, collection)[item_id]["name"] == payload["name"]


@pytest.mark.parametrize("name, collection, item, create_status", RESOURCES, ids=RESOURCE_IDS)
def test_delete_requires_organize_permission(
    api_client: TestClient,
    unique_user_fn_scoped: TestUser,
    name: str,
    collection: str,
    item: Callable[[str], str],
    create_status: int,
) -> None:
    user = unique_user_fn_scoped
    item_id = create_item(api_client, user, collection, create_status)

    set_can_organize(user, False)
    before = collection_items(api_client, user, collection)
    response = api_client.delete(item(item_id), headers=user.token)
    assert response.status_code == 403
    assert collection_items(api_client, user, collection) == before

    set_can_organize(user, True)
    response = api_client.delete(item(item_id), headers=user.token)
    assert response.status_code == 200
    assert item_id not in collection_items(api_client, user, collection)


@pytest.mark.parametrize("name, collection, create_status, method, merge_route, payload_keys", MERGES, ids=RESOURCE_IDS)
def test_merge_requires_organize_permission(
    api_client: TestClient,
    unique_user_fn_scoped: TestUser,
    name: str,
    collection: str,
    create_status: int,
    method: str,
    merge_route: str,
    payload_keys: tuple[str, str],
) -> None:
    user = unique_user_fn_scoped
    from_item = create_item(api_client, user, collection, create_status)
    to_item = create_item(api_client, user, collection, create_status)
    payload = {payload_keys[0]: from_item, payload_keys[1]: to_item}

    set_can_organize(user, False)
    before = collection_items(api_client, user, collection)
    response = api_client.request(method, merge_route, json=payload, headers=user.token)
    assert response.status_code == 403
    assert collection_items(api_client, user, collection) == before

    set_can_organize(user, True)
    response = api_client.request(method, merge_route, json=payload, headers=user.token)
    assert response.status_code == 200
    after = collection_items(api_client, user, collection)
    assert from_item not in after
    assert to_item in after


@pytest.mark.parametrize("name, collection, item, create_status", RESOURCES, ids=RESOURCE_IDS)
def test_read_endpoints_do_not_require_organize_permission(
    api_client: TestClient,
    unique_user_fn_scoped: TestUser,
    name: str,
    collection: str,
    item: Callable[[str], str],
    create_status: int,
) -> None:
    user = unique_user_fn_scoped
    item_id = create_item(api_client, user, collection, create_status)

    set_can_organize(user, False)

    items = collection_items(api_client, user, collection)
    assert item_id in items

    response = api_client.get(collection, params={"search": items[item_id]["name"]}, headers=user.token)
    assert response.status_code == 200
    assert item_id in {item["id"] for item in response.json()["items"]}

    response = api_client.get(item(item_id), headers=user.token)
    assert response.status_code == 200
    assert response.json()["id"] == item_id
