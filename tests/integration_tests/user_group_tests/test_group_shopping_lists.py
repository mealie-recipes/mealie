import random

from fastapi.testclient import TestClient

from mealie.schema.group.group_shopping_list import ShoppingListOut
from mealie.schema.recipe.recipe import Recipe
from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_shopping_lists_get_all(api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]):
    response = api_client.get(api_routes.groups_shopping_lists, headers=unique_user.token)
    assert response.status_code == 200
    all_lists = response.json()["items"]

    assert len(all_lists) == len(shopping_lists)

    known_ids = [str(model.id) for model in shopping_lists]

    for list_ in all_lists:
        assert list_["id"] in known_ids


def test_shopping_lists_create_one(api_client: TestClient, unique_user: TestUser):
    payload = {
        "name": random_string(10),
    }

    response = api_client.post(api_routes.groups_shopping_lists, json=payload, headers=unique_user.token)
    response_list = utils.assert_derserialize(response, 201)

    assert response_list["name"] == payload["name"]
    assert response_list["groupId"] == str(unique_user.group_id)


def test_shopping_lists_get_one(api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]):
    shopping_list = shopping_lists[0]

    response = api_client.get(api_routes.groups_shopping_lists_item_id(shopping_list.id), headers=unique_user.token)
    assert response.status_code == 200

    response_list = response.json()

    assert response_list["id"] == str(shopping_list.id)
    assert response_list["name"] == shopping_list.name
    assert response_list["groupId"] == str(shopping_list.group_id)


def test_shopping_lists_update_one(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    sample_list = random.choice(shopping_lists)

    payload = {
        "name": random_string(10),
        "id": str(sample_list.id),
        "groupId": str(sample_list.group_id),
        "listItems": [],
    }

    response = api_client.put(
        api_routes.groups_shopping_lists_item_id(sample_list.id), json=payload, headers=unique_user.token
    )
    assert response.status_code == 200

    response_list = response.json()

    assert response_list["id"] == str(sample_list.id)
    assert response_list["name"] == payload["name"]
    assert response_list["groupId"] == str(sample_list.group_id)


def test_shopping_lists_delete_one(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    sample_list = random.choice(shopping_lists)

    response = api_client.delete(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    assert response.status_code == 404


def test_shopping_lists_add_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)

    recipe = recipe_ingredient_only

    response = api_client.post(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id), headers=unique_user.token
    )
    assert response.status_code == 200

    # Get List and Check for Ingredients

    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = [ingredient.note for ingredient in recipe.recipe_ingredient]

    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

    # Check Recipe Reference was added with quantity 1
    refs = item["recipeReferences"]

    assert len(refs) == 1

    assert refs[0]["recipeId"] == str(recipe.id)


def test_shopping_list_add_recipe_scale(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)
    recipe = recipe_ingredient_only

    response = api_client.post(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id), headers=unique_user.token
    )

    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["recipeReferences"]) == 1
    assert as_json["recipeReferences"][0]["recipeQuantity"] == 1

    for item in as_json["listItems"]:
        assert item["quantity"] == 1
        refs = item["recipeReferences"]

        # only one reference per item
        assert len(refs) == 1

        # base recipe quantity is 1
        assert refs[0]["recipeQuantity"] == 1

        # scale was unspecified, which defaults to 1
        assert refs[0]["recipeScale"] == 1

    recipe_scale = round(random.uniform(1, 10), 5)
    payload = {"recipeIncrementQuantity": recipe_scale}

    response = api_client.post(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["recipeReferences"]) == 1
    assert as_json["recipeReferences"][0]["recipeQuantity"] == 1 + recipe_scale

    for item in as_json["listItems"]:
        assert item["quantity"] == 1 + recipe_scale
        refs = item["recipeReferences"]

        assert len(refs) == 1
        assert refs[0]["recipeQuantity"] == 1
        assert refs[0]["recipeScale"] == 1 + recipe_scale


def test_shopping_lists_remove_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)

    recipe = recipe_ingredient_only

    response = api_client.post(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id), headers=unique_user.token
    )
    assert response.status_code == 200

    # Get List and Check for Ingredients
    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = [ingredient.note for ingredient in recipe.recipe_ingredient]

    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

    # Remove Recipe
    response = api_client.delete(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id), headers=unique_user.token
    )

    # Get List and Check for Ingredients
    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)
    assert len(as_json["listItems"]) == 0
    assert len(as_json["recipeReferences"]) == 0


def test_shopping_lists_remove_recipe_multiple_quantity(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)

    recipe = recipe_ingredient_only

    for _ in range(3):
        response = api_client.post(
            api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
            headers=unique_user.token,
        )
        assert response.status_code == 200

    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = [ingredient.note for ingredient in recipe.recipe_ingredient]

    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

    # Remove Recipe
    response = api_client.delete(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id), headers=unique_user.token
    )

    # Get List and Check for Ingredients
    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    # All Items Should Still Exists
    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    # Quantity Should Equal 2 Start with 3 remove 1)
    for item in as_json["listItems"]:
        assert item["quantity"] == 2.0

    refs = as_json["recipeReferences"]
    assert len(refs) == 1
    assert refs[0]["recipeId"] == str(recipe.id)


def test_shopping_list_remove_recipe_scale(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)
    recipe = recipe_ingredient_only

    recipe_initital_scale = 100
    payload = {"recipeIncrementQuantity": recipe_initital_scale}

    # first add a bunch of quantity to the list
    response = api_client.post(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["recipeReferences"]) == 1
    assert as_json["recipeReferences"][0]["recipeQuantity"] == recipe_initital_scale

    for item in as_json["listItems"]:
        assert item["quantity"] == recipe_initital_scale
        refs = item["recipeReferences"]

        assert len(refs) == 1
        assert refs[0]["recipeQuantity"] == 1
        assert refs[0]["recipeScale"] == recipe_initital_scale

    recipe_decrement_scale = round(random.uniform(10, 90), 5)
    payload = {"recipeDecrementQuantity": recipe_decrement_scale}
    recipe_expected_scale = recipe_initital_scale - recipe_decrement_scale

    # remove some of the recipes
    response = api_client.delete(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["recipeReferences"]) == 1
    assert as_json["recipeReferences"][0]["recipeQuantity"] == recipe_expected_scale

    for item in as_json["listItems"]:
        assert item["quantity"] == recipe_expected_scale
        refs = item["recipeReferences"]

        assert len(refs) == 1
        assert refs[0]["recipeQuantity"] == 1
        assert refs[0]["recipeScale"] == recipe_expected_scale


def test_recipe_decrement_max(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)
    recipe = recipe_ingredient_only

    recipe_scale = 10
    payload = {"recipeIncrementQuantity": recipe_scale}

    # first add a bunch of quantity to the list
    response = api_client.post(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["recipeReferences"]) == 1
    assert as_json["recipeReferences"][0]["recipeQuantity"] == recipe_scale

    for item in as_json["listItems"]:
        assert item["quantity"] == recipe_scale
        refs = item["recipeReferences"]

        assert len(refs) == 1
        assert refs[0]["recipeQuantity"] == 1
        assert refs[0]["recipeScale"] == recipe_scale

    # next add a little bit more of one item
    item_additional_quantity = random_int(1, 10)
    item_json = as_json["listItems"][0]
    item_json["quantity"] += item_additional_quantity

    response = api_client.put(
        api_routes.groups_shopping_items_item_id(item["id"]), json=item_json, headers=unique_user.token
    )
    item_json = utils.assert_derserialize(response, 200)
    assert item_json["quantity"] == recipe_scale + item_additional_quantity

    # now remove way too many instances of the recipe
    payload = {"recipeDecrementQuantity": recipe_scale * 100}
    response = api_client.delete(
        api_routes.groups_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(api_routes.groups_shopping_lists_item_id(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    # check that only the original recipe quantity and its reference were removed, not the additional quantity
    assert len(as_json["recipeReferences"]) == 0
    assert len(as_json["listItems"]) == 1

    item = as_json["listItems"][0]
    assert item["quantity"] == item_additional_quantity
    assert len(item["recipeReferences"]) == 0


def test_shopping_list_extras(
    api_client: TestClient,
    unique_user: TestUser,
):
    key_str_1 = random_string()
    val_str_1 = random_string()

    key_str_2 = random_string()
    val_str_2 = random_string()

    # create a list with extras
    new_list_data: dict = {"name": random_string()}
    new_list_data["extras"] = {key_str_1: val_str_1}

    response = api_client.post(api_routes.groups_shopping_lists, json=new_list_data, headers=unique_user.token)
    list_as_json = utils.assert_derserialize(response, 201)

    # make sure the extra persists
    extras = list_as_json["extras"]
    assert key_str_1 in extras
    assert extras[key_str_1] == val_str_1

    # add more extras to the list
    list_as_json["extras"][key_str_2] = val_str_2

    response = api_client.put(
        api_routes.groups_shopping_lists_item_id(list_as_json["id"]), json=list_as_json, headers=unique_user.token
    )
    list_as_json = utils.assert_derserialize(response, 200)

    # make sure both the new extra and original extra persist
    extras = list_as_json["extras"]
    assert key_str_1 in extras
    assert key_str_2 in extras
    assert extras[key_str_1] == val_str_1
    assert extras[key_str_2] == val_str_2
