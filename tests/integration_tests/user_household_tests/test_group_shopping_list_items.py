import random
from math import ceil, floor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.schema.household.group_shopping_list import ShoppingListItemOut, ShoppingListOut
from mealie.schema.recipe.recipe_ingredient import SaveIngredientFood
from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def create_item(list_id: UUID4, **kwargs) -> dict:
    return {
        "shopping_list_id": str(list_id),
        "note": random_string(10),
        "quantity": random_int(1, 10),
        **kwargs,
    }


def serialize_list_items(list_items: list[ShoppingListItemOut]) -> list:
    as_dict = []
    for item in list_items:
        item_dict = item.model_dump(by_alias=True)
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

    response = api_client.post(api_routes.households_shopping_items, json=item, headers=unique_user.token)
    as_json = utils.assert_deserialize(response, 201)
    assert len(as_json["createdItems"]) == 1

    # Test Item is Getable
    created_item_id = as_json["createdItems"][0]["id"]
    response = api_client.get(
        api_routes.households_shopping_items_item_id(created_item_id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

    # Ensure List Id is Set
    assert as_json["shoppingListId"] == str(shopping_list.id)

    # Test Item In List
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    response_list = utils.assert_deserialize(response, 200)

    assert len(response_list["listItems"]) == 1

    # Check Item Ids
    assert response_list["listItems"][0]["id"] == created_item_id


def test_shopping_list_items_create_many(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
) -> None:
    items = [create_item(shopping_list.id) for _ in range(10)]

    response = api_client.post(
        api_routes.households_shopping_items_create_bulk,
        json=items,
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 201)
    assert len(as_json["createdItems"]) == len(items)
    assert len(as_json["updatedItems"]) == 0
    assert len(as_json["deletedItems"]) == 0

    # test items in list
    created_item_ids = [item["id"] for item in as_json["createdItems"]]
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

    # make sure the list is the correct size
    assert len(as_json["listItems"]) == len(items)

    for item in as_json["listItems"]:
        # Ensure List Id is Set
        assert item["shoppingListId"] == str(shopping_list.id)
        assert item["id"] in created_item_ids
        created_item_ids.remove(item["id"])

    # make sure we found all items
    assert not created_item_ids


def test_shopping_list_items_auto_assign_label_with_food_without_label(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
):
    database = unique_user.repos
    food = database.ingredient_foods.create(SaveIngredientFood(name=random_string(10), group_id=unique_user.group_id))

    item = create_item(shopping_list.id, food_id=str(food.id))
    response = api_client.post(api_routes.households_shopping_items, json=item, headers=unique_user.token)
    as_json = utils.assert_deserialize(response, 201)
    assert len(as_json["createdItems"]) == 1

    item_out = ShoppingListItemOut.model_validate(as_json["createdItems"][0])
    assert item_out.label_id is None
    assert item_out.label is None


def test_shopping_list_items_auto_assign_label_with_food_with_label(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
):
    database = unique_user.repos
    label = database.group_multi_purpose_labels.create({"name": random_string(10), "group_id": unique_user.group_id})
    food = database.ingredient_foods.create(
        SaveIngredientFood(name=random_string(10), group_id=unique_user.group_id, label_id=label.id)
    )

    item = create_item(shopping_list.id, food_id=str(food.id))
    response = api_client.post(api_routes.households_shopping_items, json=item, headers=unique_user.token)
    as_json = utils.assert_deserialize(response, 201)
    assert len(as_json["createdItems"]) == 1

    item_out = ShoppingListItemOut.model_validate(as_json["createdItems"][0])
    assert item_out.label_id == label.id
    assert item_out.label
    assert item_out.label.id == label.id


@pytest.mark.parametrize("use_fuzzy_name", [True, False])
def test_shopping_list_items_auto_assign_label_with_food_search(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_list: ShoppingListOut,
    use_fuzzy_name: bool,
):
    database = unique_user.repos
    label = database.group_multi_purpose_labels.create({"name": random_string(10), "group_id": unique_user.group_id})
    food = database.ingredient_foods.create(
        SaveIngredientFood(name=random_string(20), group_id=unique_user.group_id, label_id=label.id)
    )

    item = create_item(shopping_list.id)
    name = food.name
    if use_fuzzy_name:
        name = name + random_string(2)
    item["note"] = name

    response = api_client.post(api_routes.households_shopping_items, json=item, headers=unique_user.token)
    as_json = utils.assert_deserialize(response, 201)
    assert len(as_json["createdItems"]) == 1

    item_out = ShoppingListItemOut.model_validate(as_json["createdItems"][0])
    assert item_out.label_id == label.id
    assert item_out.label
    assert item_out.label.id == label.id


def test_shopping_list_items_get_one(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:
    for _ in range(3):
        item = random.choice(list_with_items.list_items)

        response = api_client.get(api_routes.households_shopping_items_item_id(item.id), headers=unique_user.token)
        assert response.status_code == 200


def test_shopping_list_items_get_all(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:
    params = {
        "page": 1,
        "perPage": -1,
        "queryFilter": f"shopping_list_id={list_with_items.id}",
    }
    response = api_client.get(api_routes.households_shopping_items, params=params, headers=unique_user.token)
    pagination_json = utils.assert_deserialize(response, 200)
    assert len(pagination_json["items"]) == len(list_with_items.list_items)


def test_shopping_list_items_get_one_404(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(api_routes.households_shopping_items_item_id(uuid4()), headers=unique_user.token)
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
            api_routes.households_shopping_items_item_id(item.id),
            json=update_data,
            headers=unique_user.token,
        )
        item_json = utils.assert_deserialize(response, 200)

        assert len(item_json["createdItems"]) == 0
        assert len(item_json["updatedItems"]) == 1
        assert len(item_json["deletedItems"]) == 0
        assert item_json["updatedItems"][0]["note"] == update_data["note"]
        assert item_json["updatedItems"][0]["quantity"] == update_data["quantity"]

    # make sure the list didn't change sizes
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(list_with_items.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["listItems"]) == len(list_with_items.list_items)


def test_shopping_list_items_update_many(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
) -> None:
    # create a bunch of items
    items = [create_item(shopping_list.id) for _ in range(10)]
    for item in items:
        item["quantity"] += 10

    response = api_client.post(
        api_routes.households_shopping_items_create_bulk,
        json=items,
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 201)
    assert len(as_json["createdItems"]) == len(items)

    # update the items and compare values
    item_quantity_map = {}
    for update_item in as_json["createdItems"]:
        update_item["quantity"] += random_int(-5, 5)
        item_quantity_map[update_item["id"]] = update_item["quantity"]

    response = api_client.put(
        api_routes.households_shopping_items,
        json=as_json["createdItems"],
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["updatedItems"]) == len(items)

    for updated_item in as_json["updatedItems"]:
        assert item_quantity_map[updated_item["id"]] == updated_item["quantity"]

    # make sure the list didn't change sizes
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["listItems"]) == len(items)


def test_shopping_list_items_update_many_reorder(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:
    list_items = list_with_items.list_items

    # reorder list in random order
    random.shuffle(list_items)

    # update item posiitons and serialize
    as_dict = []
    for i, item in enumerate(list_items):
        item.position = i
        item_dict = item.model_dump(by_alias=True)
        item_dict["shoppingListId"] = str(list_with_items.id)
        item_dict["id"] = str(item.id)
        as_dict.append(item_dict)

    # update list
    # the default serializer fails on certain complex objects, so we use FastAPI's serializer first
    as_dict = utils.jsonify(as_dict)
    response = api_client.put(api_routes.households_shopping_items, json=as_dict, headers=unique_user.token)
    assert response.status_code == 200

    # retrieve list and check positions against list
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(list_with_items.id),
        headers=unique_user.token,
    )
    response_list = utils.assert_deserialize(response, 200)

    for i, item_data in enumerate(response_list["listItems"]):
        assert item_data["position"] == i
        assert item_data["id"] == str(list_items[i].id)


def test_shopping_list_items_delete_one(
    api_client: TestClient,
    unique_user: TestUser,
    list_with_items: ShoppingListOut,
) -> None:
    item = random.choice(list_with_items.list_items)

    # Delete Item
    response = api_client.delete(api_routes.households_shopping_items_item_id(item.id), headers=unique_user.token)
    assert response.status_code == 200

    # Validate Get Item Returns 404
    response = api_client.get(api_routes.households_shopping_items_item_id(item.id), headers=unique_user.token)
    assert response.status_code == 404


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
        api_routes.households_shopping_items,
        json=serialize_list_items(list_items),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    # retrieve list and check positions against list
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(list_with_items.id),
        headers=unique_user.token,
    )
    response_list = utils.assert_deserialize(response, 200)

    assert len(response_list["listItems"]) == 1
    assert response_list["listItems"][0]["quantity"] == len(list_items)
    assert response_list["listItems"][0]["note"] == master_note


def test_shopping_list_items_add_mergeable(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
):
    # add a bunch of items that can be consolidated
    items = [create_item(shopping_list.id) for _ in range(5)]

    common_note = random_string()
    duplicate_items = [create_item(shopping_list.id) for _ in range(5)]
    for item in duplicate_items:
        item["note"] = common_note

    merged_qty = sum([item["quantity"] for item in duplicate_items])  # type: ignore

    response = api_client.post(
        api_routes.households_shopping_items_create_bulk,
        json=items + duplicate_items,
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 201)
    assert len(as_json["createdItems"]) == len(items) + 1
    assert len(as_json["updatedItems"]) == 0
    assert len(as_json["deletedItems"]) == 0

    found = False
    for item in as_json["createdItems"]:
        if item["note"] == common_note:
            assert item["quantity"] == merged_qty
            found = True
            break

    assert found

    # add more items that can be merged into the existing items
    item_to_merge_into = random.choice(as_json["createdItems"])
    new_item = create_item(shopping_list.id)
    new_item["note"] = item_to_merge_into["note"]
    updated_quantity = new_item["quantity"] + item_to_merge_into["quantity"]

    response = api_client.post(api_routes.households_shopping_items, json=new_item, headers=unique_user.token)
    item_json = utils.assert_deserialize(response, 201)

    # we should have received an updated item, not a created item
    assert len(item_json["createdItems"]) == 0
    assert len(item_json["updatedItems"]) == 1
    assert len(item_json["deletedItems"]) == 0
    assert item_json["updatedItems"][0]["id"] == item_to_merge_into["id"]
    assert item_json["updatedItems"][0]["quantity"] == updated_quantity

    # fetch the list and make sure we have the correct number of items
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    list_json = utils.assert_deserialize(response, 200)
    assert len(list_json["listItems"]) == len(as_json["createdItems"])


def test_shopping_list_items_update_mergable(
    api_client: TestClient, unique_user: TestUser, list_with_items: ShoppingListOut
):
    # update every other item so it merges into the previous item
    for i, item in enumerate(list_with_items.list_items):
        if not i % 2:
            continue

        item.note = list_with_items.list_items[i - 1].note

    payload = utils.jsonify([item.model_dump() for item in list_with_items.list_items])
    response = api_client.put(api_routes.households_shopping_items, json=payload, headers=unique_user.token)
    as_json = utils.assert_deserialize(response, 200)

    assert len(as_json["createdItems"]) == 0
    assert len(as_json["updatedItems"]) == ceil(len(list_with_items.list_items) / 2)
    assert len(as_json["deletedItems"]) == floor(len(list_with_items.list_items) / 2)

    # check that every other item was updated, and its quantity matches the sum of itself and the previous item
    for i, item in enumerate(list_with_items.list_items):
        if not i % 2:
            continue

        assert (
            as_json["updatedItems"][floor(i / 2)]["quantity"]
            == item.quantity + list_with_items.list_items[i - 1].quantity
        )

    # confirm the number of items on the list matches
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(list_with_items.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    updated_list_items = as_json["listItems"]
    assert len(updated_list_items) == ceil(len(list_with_items.list_items) / 2)

    # update two of the items so they merge into each other
    new_note = random_string()
    items_to_merge = random.sample(updated_list_items, 2)
    for item_data in items_to_merge:
        item_data["note"] = new_note

    merged_quantity = sum([item["quantity"] for item in items_to_merge])

    payload = utils.jsonify(items_to_merge)
    response = api_client.put(api_routes.households_shopping_items, json=payload, headers=unique_user.token)
    as_json = utils.assert_deserialize(response, 200)

    assert len(as_json["createdItems"]) == 0
    assert len(as_json["updatedItems"]) == 1
    assert len(as_json["deletedItems"]) == 1
    assert as_json["deletedItems"][0]["id"] in [item["id"] for item in items_to_merge]

    found = False
    for item_data in as_json["updatedItems"]:
        if item_data["id"] not in [item["id"] for item in items_to_merge]:
            continue

        assert item_data["quantity"] == merged_quantity
        found = True
        break

    assert found


def test_shopping_list_items_checked_off(
    api_client: TestClient, unique_user: TestUser, list_with_items: ShoppingListOut
):
    # rename an item to match another item and check it off, and make sure it does not affect the other item
    checked_item, reference_item = random.sample(list_with_items.list_items, 2)
    checked_item.note = reference_item.note
    checked_item.checked = True

    response = api_client.put(
        api_routes.households_shopping_items_item_id(checked_item.id),
        json=utils.jsonify(checked_item.model_dump()),
        headers=unique_user.token,
    )

    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["createdItems"]) == 0
    assert len(as_json["updatedItems"]) == 1
    assert len(as_json["deletedItems"]) == 0
    updated_item = as_json["updatedItems"][0]
    assert updated_item["checked"]

    # get the reference item and make sure it didn't change
    response = api_client.get(
        api_routes.households_shopping_items_item_id(reference_item.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    reference_item_get = ShoppingListItemOut.model_validate(as_json)

    assert reference_item_get.id == reference_item.id
    assert reference_item_get.shopping_list_id == reference_item.shopping_list_id
    assert reference_item_get.note == reference_item.note
    assert reference_item_get.quantity == reference_item.quantity
    assert reference_item_get.checked == reference_item.checked

    # rename an item to match another item and check both off, and make sure they are not merged
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(list_with_items.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    updated_list = ShoppingListOut.model_validate(as_json)

    item_1, item_2 = random.sample(updated_list.list_items, 2)
    item_1.checked = True
    item_2.checked = True
    item_2.note = item_1.note

    response = api_client.put(
        api_routes.households_shopping_items,
        json=utils.jsonify([item_1.model_dump(), item_2.model_dump()]),
        headers=unique_user.token,
    )

    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["createdItems"]) == 0
    assert len(as_json["updatedItems"]) == 2
    assert len(as_json["deletedItems"]) == 0

    updated_items_map = {item["id"]: item for item in as_json["updatedItems"]}
    for item in [item_1, item_2]:
        updated_item_data = updated_items_map[str(item.id)]
        assert item.note == updated_item_data["note"]
        assert item.quantity == updated_item_data["quantity"]
        assert updated_item_data["checked"]


def test_shopping_list_items_with_zero_quantity(
    api_client: TestClient, unique_user: TestUser, shopping_list: ShoppingListOut
):
    # add a bunch of items, some with zero quantity, and make sure they persist
    normal_items = [create_item(shopping_list.id) for _ in range(10)]
    zero_qty_items = [create_item(shopping_list.id) for _ in range(10)]
    for item in zero_qty_items:
        item["quantity"] = 0

    response = api_client.post(
        api_routes.households_shopping_items_create_bulk,
        json=normal_items + zero_qty_items,
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 201)
    assert len(as_json["createdItems"]) == len(normal_items + zero_qty_items)

    # confirm the number of items on the list matches
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    created_items = as_json["listItems"]
    assert len(created_items) == len(normal_items + zero_qty_items)

    # add another zero quantity item so it merges into the existing item
    new_item_to_merge = create_item(shopping_list.id)
    new_item_to_merge["quantity"] = 0
    target_item = random.choice(created_items)
    new_item_to_merge["note"] = target_item["note"]

    response = api_client.post(
        api_routes.households_shopping_items,
        json=new_item_to_merge,
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 201)
    assert len(as_json["createdItems"]) == 0
    assert len(as_json["updatedItems"]) == 1
    assert len(as_json["deletedItems"]) == 0

    updated_item = as_json["updatedItems"][0]
    assert updated_item["id"] == target_item["id"]
    assert updated_item["note"] == target_item["note"]
    assert updated_item["quantity"] == target_item["quantity"]

    # confirm the number of items on the list stayed the same
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["listItems"]) == len(normal_items + zero_qty_items)

    # update an existing item to zero quantity and make sure it merges into the existing item
    update_item_to_merge, target_item = random.sample(as_json["listItems"], 2)
    update_item_to_merge["note"] = target_item["note"]
    update_item_to_merge["quantity"] = 0

    response = api_client.put(
        api_routes.households_shopping_items_item_id(update_item_to_merge["id"]),
        json=update_item_to_merge,
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["createdItems"]) == 0
    assert len(as_json["updatedItems"]) == 1
    assert len(as_json["deletedItems"]) == 1
    assert as_json["deletedItems"][0]["id"] == update_item_to_merge["id"]

    updated_item = as_json["updatedItems"][0]
    assert updated_item["id"] == target_item["id"]
    assert updated_item["note"] == target_item["note"]
    assert updated_item["quantity"] == target_item["quantity"]

    # confirm the number of items on the list shrunk by one
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["listItems"]) == len(normal_items + zero_qty_items) - 1


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

    response = api_client.post(api_routes.households_shopping_items, json=new_item_data, headers=unique_user.token)
    collection = utils.assert_deserialize(response, 201)
    item_as_json = collection["createdItems"][0]

    # make sure the extra persists
    extras = item_as_json["extras"]
    assert key_str_1 in extras
    assert extras[key_str_1] == val_str_1

    # add more extras to the item
    item_as_json["extras"][key_str_2] = val_str_2

    response = api_client.put(
        api_routes.households_shopping_items_item_id(item_as_json["id"]),
        json=item_as_json,
        headers=unique_user.token,
    )
    collection = utils.assert_deserialize(response, 200)
    item_as_json = collection["updatedItems"][0]

    # make sure both the new extra and original extra persist
    extras = item_as_json["extras"]
    assert key_str_1 in extras
    assert key_str_2 in extras
    assert extras[key_str_1] == val_str_1
    assert extras[key_str_2] == val_str_2
