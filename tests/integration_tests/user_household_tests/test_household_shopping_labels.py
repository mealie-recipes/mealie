from uuid import uuid4

from fastapi.testclient import TestClient

from mealie.schema.household.group_shopping_list import ShoppingListOut
from tests.utils import api_routes, assert_deserialize
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def set_can_organize(user: TestUser, value: bool) -> None:
    db_user = user.repos.users.get_one(user.user_id)
    assert db_user
    db_user.can_organize = value
    user.repos.users.update(db_user.id, db_user)


def create_label(api_client: TestClient, user: TestUser, **overrides) -> dict:
    payload = {"name": random_string(), "color": "#ff0000", **overrides}
    response = api_client.post(api_routes.households_shopping_labels, json=payload, headers=user.token)
    return assert_deserialize(response, 201)


def create_items(api_client: TestClient, user: TestUser, shopping_list: ShoppingListOut, count: int = 3) -> list[dict]:
    payload = [{"shoppingListId": str(shopping_list.id), "note": random_string(), "position": i} for i in range(count)]
    response = api_client.post(api_routes.households_shopping_items_create_bulk, json=payload, headers=user.token)
    return assert_deserialize(response, 201)["createdItems"]


def get_item(api_client: TestClient, user: TestUser, item_id: str) -> dict:
    response = api_client.get(api_routes.households_shopping_items_item_id(item_id), headers=user.token)
    return assert_deserialize(response, 200)


def test_shopping_label_crud(api_client: TestClient, unique_user: TestUser):
    label = create_label(api_client, unique_user, sortOrder=2)
    assert label["householdId"] == str(unique_user.household_id)
    assert label["sortOrder"] == 2

    response = api_client.get(api_routes.households_shopping_labels_label_id(label["id"]), headers=unique_user.token)
    assert assert_deserialize(response, 200)["name"] == label["name"]

    response = api_client.get(api_routes.households_shopping_labels, params={"perPage": -1}, headers=unique_user.token)
    assert label["id"] in [item["id"] for item in assert_deserialize(response, 200)["items"]]

    update = {**label, "name": random_string(), "color": "#00ff00"}
    response = api_client.put(
        api_routes.households_shopping_labels_label_id(label["id"]), json=update, headers=unique_user.token
    )
    updated = assert_deserialize(response, 200)
    assert updated["name"] == update["name"]
    assert updated["color"] == "#00ff00"

    response = api_client.delete(api_routes.households_shopping_labels_label_id(label["id"]), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(api_routes.households_shopping_labels_label_id(label["id"]), headers=unique_user.token)
    assert response.status_code == 404


def test_shopping_label_get_unknown_returns_404(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(api_routes.households_shopping_labels_label_id(uuid4()), headers=unique_user.token)
    assert response.status_code == 404


def test_shopping_label_duplicate_name_returns_409(api_client: TestClient, unique_user: TestUser):
    label = create_label(api_client, unique_user)

    response = api_client.post(
        api_routes.households_shopping_labels, json={"name": label["name"]}, headers=unique_user.token
    )
    assert response.status_code == 409

    other = create_label(api_client, unique_user)
    response = api_client.put(
        api_routes.households_shopping_labels_label_id(other["id"]),
        json={**other, "name": label["name"]},
        headers=unique_user.token,
    )
    assert response.status_code == 409


def test_shopping_labels_are_scoped_to_household(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    set_can_organize(h2_user, True)
    label = create_label(api_client, unique_user)

    response = api_client.get(api_routes.households_shopping_labels_label_id(label["id"]), headers=h2_user.token)
    assert response.status_code == 404

    response = api_client.get(api_routes.households_shopping_labels, params={"perPage": -1}, headers=h2_user.token)
    assert label["id"] not in [item["id"] for item in assert_deserialize(response, 200)["items"]]

    # the same name may be used by another household
    response = api_client.post(
        api_routes.households_shopping_labels, json={"name": label["name"]}, headers=h2_user.token
    )
    assert response.status_code == 201

    response = api_client.delete(api_routes.households_shopping_labels_label_id(label["id"]), headers=h2_user.token)
    assert response.status_code == 404


def test_shopping_label_write_requires_organize_permission(
    api_client: TestClient, unique_user: TestUser, unprivileged_user: TestUser
):
    label = create_label(api_client, unique_user)

    response = api_client.post(
        api_routes.households_shopping_labels, json={"name": random_string()}, headers=unprivileged_user.token
    )
    assert response.status_code == 403

    response = api_client.put(
        api_routes.households_shopping_labels_label_id(label["id"]), json=label, headers=unprivileged_user.token
    )
    assert response.status_code == 403

    response = api_client.delete(
        api_routes.households_shopping_labels_label_id(label["id"]), headers=unprivileged_user.token
    )
    assert response.status_code == 403

    response = api_client.get(api_routes.households_shopping_labels, headers=unprivileged_user.token)
    assert response.status_code == 200


def test_shopping_label_system_label_is_protected(api_client: TestClient, unique_user: TestUser):
    label = create_label(api_client, unique_user, isSystem=True)

    response = api_client.delete(api_routes.households_shopping_labels_label_id(label["id"]), headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.put(
        api_routes.households_shopping_labels_label_id(label["id"]),
        json={**label, "isSystem": False},
        headers=unique_user.token,
    )
    assert response.status_code == 403


def test_shopping_item_patch_label_and_position(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
):
    label = create_label(api_client, unique_user)
    item = create_items(api_client, unique_user, shopping_list, count=1)[0]

    response = api_client.patch(
        api_routes.households_shopping_items_item_id(item["id"]),
        json={"position": 5, "shoppingLabelId": label["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    updated = get_item(api_client, unique_user, item["id"])
    assert updated["position"] == 5
    assert updated["shoppingLabelId"] == label["id"]

    # omitting the label leaves it untouched
    response = api_client.patch(
        api_routes.households_shopping_items_item_id(item["id"]), json={"position": 1}, headers=unique_user.token
    )
    assert response.status_code == 200
    updated = get_item(api_client, unique_user, item["id"])
    assert updated["position"] == 1
    assert updated["shoppingLabelId"] == label["id"]

    # an explicit null removes it
    response = api_client.patch(
        api_routes.households_shopping_items_item_id(item["id"]),
        json={"shoppingLabelId": None},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    updated = get_item(api_client, unique_user, item["id"])
    assert updated["position"] == 1
    assert updated["shoppingLabelId"] is None


def test_shopping_item_patch_unknown_item_returns_404(api_client: TestClient, unique_user: TestUser):
    response = api_client.patch(
        api_routes.households_shopping_items_item_id(uuid4()), json={"position": 1}, headers=unique_user.token
    )
    assert response.status_code == 404


def test_shopping_list_reorder(api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut):
    label = create_label(api_client, unique_user)
    items = create_items(api_client, unique_user, shopping_list, count=3)

    changes = [
        {"itemId": items[0]["id"], "position": 2, "labelId": label["id"]},
        {"itemId": items[1]["id"], "position": 0},
        {"itemId": items[2]["id"], "position": 1, "labelId": label["id"]},
    ]
    response = api_client.patch(
        api_routes.households_shopping_lists_list_id_reorder(shopping_list.id),
        json=changes,
        headers=unique_user.token,
    )
    assert response.status_code == 200

    reordered = {item["id"]: get_item(api_client, unique_user, item["id"]) for item in items}
    assert [reordered[item["id"]]["position"] for item in items] == [2, 0, 1]
    assert [reordered[item["id"]]["shoppingLabelId"] for item in items] == [label["id"], None, label["id"]]


def test_shopping_list_reorder_unknown_list_returns_404(api_client: TestClient, unique_user: TestUser):
    response = api_client.patch(
        api_routes.households_shopping_lists_list_id_reorder(uuid4()), json=[], headers=unique_user.token
    )
    assert response.status_code == 404


def test_shopping_list_reorder_ignores_items_from_other_lists(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    first_list, second_list = shopping_lists[:2]
    item = create_items(api_client, unique_user, second_list, count=1)[0]

    response = api_client.patch(
        api_routes.households_shopping_lists_list_id_reorder(first_list.id),
        json=[{"itemId": item["id"], "position": 9}],
        headers=unique_user.token,
    )
    assert response.status_code == 200
    assert get_item(api_client, unique_user, item["id"])["position"] == item["position"]


def test_shopping_list_reorder_other_household_returns_404(
    api_client: TestClient, h2_user: TestUser, shopping_list: ShoppingListOut
):
    response = api_client.patch(
        api_routes.households_shopping_lists_list_id_reorder(shopping_list.id),
        json=[],
        headers=h2_user.token,
    )
    assert response.status_code == 404


def test_delete_label_clears_it_from_items(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
):
    label = create_label(api_client, unique_user)
    item = create_items(api_client, unique_user, shopping_list, count=1)[0]
    response = api_client.patch(
        api_routes.households_shopping_items_item_id(item["id"]),
        json={"shoppingLabelId": label["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response = api_client.delete(api_routes.households_shopping_labels_label_id(label["id"]), headers=unique_user.token)
    assert response.status_code == 200

    remaining = get_item(api_client, unique_user, item["id"])
    assert remaining["shoppingLabelId"] is None
