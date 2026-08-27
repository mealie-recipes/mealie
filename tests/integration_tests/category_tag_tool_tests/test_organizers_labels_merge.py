"""
Integration tests for:
- GET /groups/labels/empty
- POST /groups/labels/merge

Labels aren't linked to recipes directly; they're referenced from foods and from
shopping list items (plus a per-shopping-list "label settings" row created for every
label in the group). Merge has to reassign all three, and de-duplicate the
label-settings row the same way tag/category merge de-duplicates overlapping
recipe associations.
"""

import uuid

from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

LABELS_MERGE = "/api/groups/labels/merge"


def _create_label(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(api_routes.groups_labels, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 200
    return response.json()


def _create_food(api_client: TestClient, user: TestUser, label_id: str | None = None) -> dict:
    data = CreateIngredientFood(name=random_string(10), label_id=label_id).model_dump(by_alias=True)
    response = api_client.post(api_routes.foods, json=data, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _create_shopping_list(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string(10)}, headers=user.token
    )
    assert response.status_code == 201
    return response.json()


def _create_shopping_list_item(api_client: TestClient, user: TestUser, list_id: str, label_id: str) -> dict:
    response = api_client.post(
        api_routes.households_shopping_items,
        json={"shoppingListId": list_id, "labelId": label_id, "note": random_string(10)},
        headers=user.token,
    )
    assert response.status_code == 201
    return response.json()["createdItems"][0]


# ---------------------------------------------------------------------------
# Labels — empty
# ---------------------------------------------------------------------------


def test_labels_empty_includes_unused_label_and_excludes_used_label(api_client: TestClient, unique_user: TestUser):
    unused_label = _create_label(api_client, unique_user)
    used_label = _create_label(api_client, unique_user)
    food = _create_food(api_client, unique_user, label_id=used_label["id"])

    response = api_client.get(api_routes.groups_labels_empty, headers=unique_user.token)
    assert response.status_code == 200
    ids = [label["id"] for label in response.json()]
    assert unused_label["id"] in ids
    assert used_label["id"] not in ids

    api_client.delete(api_routes.foods_item_id(food["id"]), headers=unique_user.token)
    api_client.delete(api_routes.groups_labels_item_id(unused_label["id"]), headers=unique_user.token)
    api_client.delete(api_routes.groups_labels_item_id(used_label["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Labels — merge
# ---------------------------------------------------------------------------


def test_label_merge_reassigns_foods_and_shopping_list_items(api_client: TestClient, unique_user: TestUser):
    from_label = _create_label(api_client, unique_user)
    to_label = _create_label(api_client, unique_user)

    food = _create_food(api_client, unique_user, label_id=from_label["id"])

    # creating a shopping list auto-creates a label-settings row for every existing label,
    # so this list has settings rows for both from_label and to_label already.
    shopping_list = _create_shopping_list(api_client, unique_user)
    item = _create_shopping_list_item(api_client, unique_user, shopping_list["id"], from_label["id"])

    response = api_client.post(
        LABELS_MERGE,
        json={"fromId": from_label["id"], "toId": to_label["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == to_label["id"]

    # from_label must be deleted
    assert (
        api_client.get(api_routes.groups_labels_item_id(from_label["id"]), headers=unique_user.token).status_code == 404
    )

    # food must now point at to_label
    food_after = api_client.get(api_routes.foods_item_id(food["id"]), headers=unique_user.token).json()
    assert food_after["label"]["id"] == to_label["id"]

    # shopping list item must now point at to_label
    item_after = api_client.get(
        api_routes.households_shopping_items_item_id(item["id"]), headers=unique_user.token
    ).json()
    assert item_after["labelId"] == to_label["id"]

    # the shopping list's label settings must have de-duplicated down to a single
    # row for to_label, with no dangling row still pointing at the deleted from_label
    list_after = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list["id"]), headers=unique_user.token
    ).json()
    label_setting_ids = [setting["labelId"] for setting in list_after["labelSettings"]]
    assert label_setting_ids.count(to_label["id"]) == 1
    assert from_label["id"] not in label_setting_ids

    api_client.delete(api_routes.households_shopping_lists_item_id(shopping_list["id"]), headers=unique_user.token)
    api_client.delete(api_routes.foods_item_id(food["id"]), headers=unique_user.token)
    api_client.delete(api_routes.groups_labels_item_id(to_label["id"]), headers=unique_user.token)


def test_label_merge_unknown_from_id_returns_404(api_client: TestClient, unique_user: TestUser):
    to_label = _create_label(api_client, unique_user)
    response = api_client.post(
        LABELS_MERGE,
        json={"fromId": str(uuid.uuid4()), "toId": to_label["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 404

    api_client.delete(api_routes.groups_labels_item_id(to_label["id"]), headers=unique_user.token)


def test_label_merge_same_id_returns_400(api_client: TestClient, unique_user: TestUser):
    label = _create_label(api_client, unique_user)
    response = api_client.post(
        LABELS_MERGE,
        json={"fromId": label["id"], "toId": label["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 400

    api_client.delete(api_routes.groups_labels_item_id(label["id"]), headers=unique_user.token)
