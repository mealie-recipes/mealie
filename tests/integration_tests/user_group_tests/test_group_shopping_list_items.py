import random
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.schema.group.group_shopping_list import ShoppingListItemOut, ShoppingListOut
from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def create_item(list_id: UUID4) -> dict:
    return {
        "shopping_list_id": str(list_id),
        "checked": False,
        "position": 0,
        "is_food": False,
        "note": random_string(10),
        "quantity": 1,
        "unit_id": None,
        "unit": None,
        "food_id": None,
        "food": None,
        "recipe_id": None,
        "label_id": None,
    }


def serialize_list_items(list_items: list[ShoppingListItemOut]) -> list:
    as_dict = []
    for item in list_items:
        item_dict = item.dict(by_alias=True)
        item_dict["shoppingListId"] = str(item.shopping_list_id)
        item_dict["id"] = str(item.id)
        as_dict.append(item_dict)

    # the default serializer fails on certain complex objects, so we use FastAPI's serliazer first
    as_dict = utils.jsonify(as_dict)
    return as_dict


def test_shopping_list_items_create_one(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
) -> None:
    item = create_item(shopping_list.id)

    response = api_client.post(api_routes.groups_shopping_items, json=item, headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 201)

    # Test Item is Getable
    created_item_id = as_json["id"]
    response = api_client.get(api_routes.groups_shopping_items_item_id(created_item_id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    # Ensure List Id is Set
    assert as_json["shoppingListId"] == str(shopping_list.id)

    # Test Item In List
    response = api_client.get(api_routes.groups_shopping_lists_item_id(shopping_list.id), headers=unique_user.token)
    response_list = utils.assert_derserialize(response, 200)

    assert len(response_list["listItems"]) == 1

    # Check Item Id's
    assert response_list["listItems"][0]["id"] == created_item_id


def test_shopping_list_items_get_one(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:

    for _ in range(3):
        item = random.choice(list_with_items.list_items)

        response = api_client.get(api_routes.groups_shopping_items_item_id(item.id), headers=unique_user.token)
        assert response.status_code == 200


def test_shopping_list_items_get_one_404(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(api_routes.groups_shopping_items_item_id(uuid4()), headers=unique_user.token)
    assert response.status_code == 404


def test_shopping_list_items_update_one(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:
    for _ in range(3):
        item = random.choice(list_with_items.list_items)

        item.note = random_string(10)

        update_data = create_item(list_with_items.id)
        update_data["id"] = str(item.id)

        response = api_client.put(
            api_routes.groups_shopping_items_item_id(item.id), json=update_data, headers=unique_user.token
        )
        item_json = utils.assert_derserialize(response, 200)
        assert item_json["note"] == update_data["note"]


def test_shopping_list_items_delete_one(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:
    item = random.choice(list_with_items.list_items)

    # Delete Item
    response = api_client.delete(api_routes.groups_shopping_items_item_id(item.id), headers=unique_user.token)
    assert response.status_code == 200

    # Validate Get Item Returns 404
    response = api_client.get(api_routes.groups_shopping_items_item_id(item.id), headers=unique_user.token)
    assert response.status_code == 404


def test_shopping_list_items_update_many(api_client: TestClient, unique_user: TestUser) -> None:
    assert True


def test_shopping_list_items_update_many_reorder(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:
    list_items = list_with_items.list_items

    # reorder list in random order
    random.shuffle(list_items)

    # update List posiitons and serialize
    as_dict = []
    for i, item in enumerate(list_items):
        item.position = i
        item_dict = item.dict(by_alias=True)
        item_dict["shoppingListId"] = str(list_with_items.id)
        item_dict["id"] = str(item.id)
        as_dict.append(item_dict)

    # update list
    # the default serializer fails on certain complex objects, so we use FastAPI's serliazer first
    as_dict = utils.jsonify(as_dict)
    response = api_client.put(api_routes.groups_shopping_items, json=as_dict, headers=unique_user.token)
    assert response.status_code == 200

    # retrieve list and check positions against list
    response = api_client.get(api_routes.groups_shopping_lists_item_id(list_with_items.id), headers=unique_user.token)
    response_list = utils.assert_derserialize(response, 200)

    for i, item_data in enumerate(response_list["listItems"]):
        assert item_data["position"] == i
        assert item_data["id"] == str(list_items[i].id)


def test_shopping_list_items_update_many_consolidates_common_items(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:
    list_items = list_with_items.list_items

    master_note = random_string(10)

    # set quantity and note to trigger consolidation
    for li in list_items:
        li.quantity = 1
        li.note = master_note

    # update list
    response = api_client.put(
        api_routes.groups_shopping_items, json=serialize_list_items(list_items), headers=unique_user.token
    )
    assert response.status_code == 200

    # retrieve list and check positions against list
    response = api_client.get(api_routes.groups_shopping_lists_item_id(list_with_items.id), headers=unique_user.token)
    response_list = utils.assert_derserialize(response, 200)

    assert len(response_list["listItems"]) == 1
    assert response_list["listItems"][0]["quantity"] == len(list_items)
    assert response_list["listItems"][0]["note"] == master_note


@pytest.mark.skip("TODO: Implement")
def test_shopping_list_items_update_many_remove_recipe_with_other_items(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:
    # list_items = list_with_items.list_items
    pass


def test_shopping_list_item_extras(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
) -> None:
    key_str_1 = random_string()
    val_str_1 = random_string()

    key_str_2 = random_string()
    val_str_2 = random_string()

    # create an item with extras
    new_item_data = create_item(shopping_list.id)
    new_item_data["extras"] = {key_str_1: val_str_1}

    response = api_client.post(api_routes.groups_shopping_items, json=new_item_data, headers=unique_user.token)
    item_as_json = utils.assert_derserialize(response, 201)

    # make sure the extra persists
    extras = item_as_json["extras"]
    assert key_str_1 in extras
    assert extras[key_str_1] == val_str_1

    # add more extras to the item
    item_as_json["extras"][key_str_2] = val_str_2

    response = api_client.put(
        api_routes.groups_shopping_items_item_id(item_as_json["id"]), json=item_as_json, headers=unique_user.token
    )
    item_as_json = utils.assert_derserialize(response, 200)

    # make sure both the new extra and original extra persist
    extras = item_as_json["extras"]
    assert key_str_1 in extras
    assert key_str_2 in extras
    assert extras[key_str_1] == val_str_1
    assert extras[key_str_2] == val_str_2
