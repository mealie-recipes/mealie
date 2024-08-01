import random

from fastapi.testclient import TestClient

from mealie.schema.household.group_shopping_list import (
    ShoppingListItemOut,
    ShoppingListItemUpdate,
    ShoppingListItemUpdateBulk,
    ShoppingListOut,
)
from mealie.schema.recipe.recipe import Recipe
from tests import utils
from tests.utils import api_routes
from tests.utils.assertion_helpers import assert_deserialize
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_shopping_lists_get_all(api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]):
    response = api_client.get(api_routes.households_shopping_lists, headers=unique_user.token)
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

    response = api_client.post(api_routes.households_shopping_lists, json=payload, headers=unique_user.token)
    response_list = utils.assert_deserialize(response, 201)

    assert response_list["name"] == payload["name"]
    assert response_list["groupId"] == str(unique_user.group_id)
    assert response_list["householdId"] == str(unique_user.household_id)
    assert response_list["userId"] == str(unique_user.user_id)


def test_shopping_lists_get_one(api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]):
    shopping_list = shopping_lists[0]

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response_list = response.json()

    assert response_list["id"] == str(shopping_list.id)
    assert response_list["name"] == shopping_list.name
    assert response_list["groupId"] == str(shopping_list.group_id)
    assert response_list["householdId"] == str(unique_user.household_id)
    assert response_list["userId"] == str(shopping_list.user_id)


def test_shopping_lists_update_one(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    sample_list = random.choice(shopping_lists)

    payload = {
        "name": random_string(10),
        "id": str(sample_list.id),
        "groupId": str(sample_list.group_id),
        "householdId": str(sample_list.household_id),
        "userId": str(sample_list.user_id),
        "listItems": [],
    }

    response = api_client.put(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        json=payload,
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response_list = response.json()

    assert response_list["id"] == str(sample_list.id)
    assert response_list["name"] == payload["name"]
    assert response_list["groupId"] == str(sample_list.group_id)
    assert response_list["householdId"] == str(sample_list.household_id)
    assert response_list["userId"] == str(sample_list.user_id)


def test_shopping_lists_delete_one(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    sample_list = random.choice(shopping_lists)

    response = api_client.delete(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
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
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    # get list and verify items against ingredients
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = {ingredient.note: ingredient for ingredient in recipe.recipe_ingredient}
    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

        ingredient = known_ingredients[item["note"]]
        assert item["quantity"] == (ingredient.quantity or 0)

    # check recipe reference was added with quantity 1
    refs = as_json["recipeReferences"]
    assert len(refs) == 1
    assert refs[0]["recipeId"] == str(recipe.id)
    assert refs[0]["recipeQuantity"] == 1

    # add the recipe again and check the resulting items
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

        ingredient = known_ingredients[item["note"]]
        assert item["quantity"] == (ingredient.quantity or 0) * 2

    refs = as_json["recipeReferences"]
    assert len(refs) == 1
    assert refs[0]["recipeId"] == str(recipe.id)
    assert refs[0]["recipeQuantity"] == 2


def test_shopping_lists_add_one_with_zero_quantity(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
):
    shopping_list = random.choice(shopping_lists)

    # build a recipe that has some ingredients with a null quantity
    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=unique_user.token)
    recipe_slug = utils.assert_deserialize(response, 201)

    response = api_client.get(f"{api_routes.recipes}/{recipe_slug}", headers=unique_user.token)
    recipe_data = utils.assert_deserialize(response, 200)

    ingredient_1 = {"quantity": random_int(1, 10), "note": random_string()}
    ingredient_2 = {"quantity": random_int(1, 10), "note": random_string()}
    ingredient_3_null_qty = {"quantity": None, "note": random_string()}

    recipe_data["recipeIngredient"] = [
        ingredient_1,
        ingredient_2,
        ingredient_3_null_qty,
    ]
    response = api_client.put(
        f"{api_routes.recipes}/{recipe_slug}",
        json=recipe_data,
        headers=unique_user.token,
    )
    utils.assert_deserialize(response, 200)

    recipe = Recipe.model_validate_json(
        api_client.get(f"{api_routes.recipes}/{recipe_slug}", headers=unique_user.token).content
    )
    assert recipe.id
    assert len(recipe.recipe_ingredient) == 3

    # add the recipe to the list and make sure there are three list items
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(shopping_list.id, recipe.id),
        headers=unique_user.token,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    shopping_list_out = ShoppingListOut.model_validate(utils.assert_deserialize(response, 200))

    assert len(shopping_list_out.list_items) == 3

    found = False
    for item in shopping_list_out.list_items:
        if item.note != ingredient_3_null_qty["note"]:
            continue

        found = True
        assert item.quantity == 0

    assert found


def test_shopping_lists_add_custom_recipe_items(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)
    recipe = recipe_ingredient_only

    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    custom_items = random.sample(recipe_ingredient_only.recipe_ingredient, k=3)
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
        json={"recipeIngredients": utils.jsonify(custom_items)},
    )
    assert response.status_code == 200

    # get list and verify items against ingredients
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = {ingredient.note: ingredient for ingredient in recipe.recipe_ingredient}
    custom_ingredients = [ingredient.note for ingredient in custom_items]
    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

        ingredient = known_ingredients[item["note"]]
        if item["note"] in custom_ingredients:
            assert item["quantity"] == (ingredient.quantity * 2 if ingredient.quantity else 0)

        else:
            assert item["quantity"] == (ingredient.quantity or 0)

    # check recipe reference was added with quantity 2
    refs = as_json["recipeReferences"]
    assert len(refs) == 1
    assert refs[0]["recipeId"] == str(recipe.id)
    assert refs[0]["recipeQuantity"] == 2


def test_shopping_list_ref_removes_itself(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_list: ShoppingListOut,
    recipe_ingredient_only: Recipe,
):
    # add a recipe to a list, then check off all recipe items and make sure the recipe ref is deleted
    recipe = recipe_ingredient_only
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(shopping_list.id, recipe.id),
        headers=unique_user.token,
    )
    utils.assert_deserialize(response, 200)

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    shopping_list_json = utils.assert_deserialize(response, 200)
    assert len(shopping_list_json["listItems"]) == len(recipe.recipe_ingredient)
    assert len(shopping_list_json["recipeReferences"]) == 1

    for item in shopping_list_json["listItems"]:
        item["checked"] = True

    response = api_client.put(
        api_routes.households_shopping_items,
        json=shopping_list_json["listItems"],
        headers=unique_user.token,
    )
    utils.assert_deserialize(response, 200)

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    shopping_list_json = utils.assert_deserialize(response, 200)
    assert len(shopping_list_json["recipeReferences"]) == 0


def test_shopping_lists_add_recipe_with_merge(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
):
    shopping_list = random.choice(shopping_lists)

    # build a recipe that has some ingredients more than once
    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=unique_user.token)
    recipe_slug = utils.assert_deserialize(response, 201)

    response = api_client.get(f"{api_routes.recipes}/{recipe_slug}", headers=unique_user.token)
    recipe_data = utils.assert_deserialize(response, 200)

    ingredient_1 = {"quantity": random_int(1, 10), "note": random_string()}
    ingredient_2 = {"quantity": random_int(1, 10), "note": random_string()}
    ingredient_duplicate_1 = {"quantity": random_int(1, 10), "note": random_string()}
    ingredient_duplicate_2 = {
        "quantity": random_int(1, 10),
        "note": ingredient_duplicate_1["note"],
    }

    recipe_data["recipeIngredient"] = [
        ingredient_1,
        ingredient_2,
        ingredient_duplicate_1,
        ingredient_duplicate_2,
    ]
    response = api_client.put(
        f"{api_routes.recipes}/{recipe_slug}",
        json=recipe_data,
        headers=unique_user.token,
    )
    utils.assert_deserialize(response, 200)

    recipe = Recipe.model_validate_json(
        api_client.get(f"{api_routes.recipes}/{recipe_slug}", headers=unique_user.token).content
    )
    assert recipe.id
    assert len(recipe.recipe_ingredient) == 4

    # add the recipe to the list and make sure there are only three list items, and their quantities/refs are correct
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(shopping_list.id, recipe.id),
        headers=unique_user.token,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    shopping_list_out = ShoppingListOut.model_validate(utils.assert_deserialize(response, 200))

    assert len(shopping_list_out.list_items) == 3

    found_item_1 = False
    found_item_2 = False
    found_duplicate_item = False
    for list_item in shopping_list_out.list_items:
        assert len(list_item.recipe_references) == 1

        ref = list_item.recipe_references[0]
        assert ref.recipe_scale == 1
        assert ref.recipe_quantity == list_item.quantity

        if list_item.note == ingredient_1["note"]:
            assert list_item.quantity == ingredient_1["quantity"]
            found_item_1 = True

        elif list_item.note == ingredient_2["note"]:
            assert list_item.quantity == ingredient_2["quantity"]
            found_item_2 = True

        elif list_item.note == ingredient_duplicate_1["note"]:
            combined_quantity = ingredient_duplicate_1["quantity"] + ingredient_duplicate_2["quantity"]  # type: ignore
            assert list_item.quantity == combined_quantity
            found_duplicate_item = True

    assert all([found_item_1, found_item_2, found_duplicate_item])


def test_shopping_list_add_recipe_scale(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)
    recipe = recipe_ingredient_only

    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

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
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

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

    # add two instances of the recipe
    payload = {"recipeIncrementQuantity": 2}
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        json=payload,
        headers=unique_user.token,
    )
    assert response.status_code == 200

    # remove one instance of the recipe
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id_delete(sample_list.id, recipe.id),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    # get list and verify items against ingredients
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = {ingredient.note: ingredient for ingredient in recipe.recipe_ingredient}
    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

        ingredient = known_ingredients[item["note"]]
        assert item["quantity"] == (ingredient.quantity or 0)

    # check recipe reference was reduced to 1
    refs = as_json["recipeReferences"]
    assert len(refs) == 1
    assert refs[0]["recipeId"] == str(recipe.id)
    assert refs[0]["recipeQuantity"] == 1

    # remove the recipe again and check if the list is empty
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id_delete(sample_list.id, recipe.id),
        headers=unique_user.token,
    )
    assert response.status_code == 200

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
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
            api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
            headers=unique_user.token,
        )
        assert response.status_code == 200

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = [ingredient.note for ingredient in recipe.recipe_ingredient]

    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

    # Remove Recipe
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id_delete(sample_list.id, recipe.id),
        headers=unique_user.token,
    )

    # Get List and Check for Ingredients
    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

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
    payload: dict = {"recipeIncrementQuantity": recipe_initital_scale}

    # first add a bunch of quantity to the list
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

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
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id_delete(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

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
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

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
    item_json = random.choice(as_json["listItems"])
    item_json["quantity"] += item_additional_quantity

    response = api_client.put(
        api_routes.households_shopping_items_item_id(item_json["id"]),
        json=item_json,
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)
    item_json = as_json["updatedItems"][0]
    assert item_json["quantity"] == recipe_scale + item_additional_quantity

    # now remove way too many instances of the recipe
    payload = {"recipeDecrementQuantity": recipe_scale * 100}
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id_delete(sample_list.id, recipe.id),
        headers=unique_user.token,
        json=payload,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(sample_list.id),
        headers=unique_user.token,
    )
    as_json = utils.assert_deserialize(response, 200)

    # check that only the original recipe quantity and its reference were removed, not the additional quantity
    assert len(as_json["recipeReferences"]) == 0
    assert len(as_json["listItems"]) == 1

    item = as_json["listItems"][0]
    assert item["quantity"] == item_additional_quantity
    assert len(item["recipeReferences"]) == 0


def test_recipe_manipulation_with_zero_quantities(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
):
    shopping_list = random.choice(shopping_lists)

    # create a recipe with one item that has a quantity of zero
    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=unique_user.token)
    recipe_slug = utils.assert_deserialize(response, 201)

    response = api_client.get(f"{api_routes.recipes}/{recipe_slug}", headers=unique_user.token)
    recipe_data = utils.assert_deserialize(response, 200)

    note_with_zero_quantity = random_string()
    recipe_data["recipeIngredient"] = [
        {"quantity": random_int(1, 10), "note": random_string()},
        {"quantity": random_int(1, 10), "note": random_string()},
        {"quantity": random_int(1, 10), "note": random_string()},
        {"quantity": 0, "note": note_with_zero_quantity},
    ]

    response = api_client.put(
        f"{api_routes.recipes}/{recipe_slug}",
        json=recipe_data,
        headers=unique_user.token,
    )
    utils.assert_deserialize(response, 200)

    recipe = Recipe.model_validate_json(
        api_client.get(f"{api_routes.recipes}/{recipe_slug}", headers=unique_user.token).content
    )
    assert recipe.id
    assert len(recipe.recipe_ingredient) == 4

    # add the recipe to the list twice and make sure the quantity is still zero
    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(shopping_list.id, recipe.id),
        headers=unique_user.token,
    )
    utils.assert_deserialize(response, 200)

    response = api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id(shopping_list.id, recipe.id),
        headers=unique_user.token,
    )
    utils.assert_deserialize(response, 200)

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    updated_list = ShoppingListOut.model_validate_json(response.content)
    assert len(updated_list.list_items) == 4

    found = False
    for item in updated_list.list_items:
        if item.note != note_with_zero_quantity:
            continue

        assert item.quantity == 0

        recipe_ref = item.recipe_references[0]
        assert recipe_ref.recipe_scale == 2

        found = True
        break

    if not found:
        raise Exception("Did not find item with no quantity in shopping list")

    # remove the recipe once and make sure the item is still on the list
    api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id_delete(shopping_list.id, recipe.id),
        headers=unique_user.token,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    updated_list = ShoppingListOut.model_validate_json(response.content)
    assert len(updated_list.list_items) == 4

    found = False
    for item in updated_list.list_items:
        if item.note != note_with_zero_quantity:
            continue

        assert item.quantity == 0

        recipe_ref = item.recipe_references[0]
        assert recipe_ref.recipe_scale == 1

        found = True
        break

    if not found:
        raise Exception("Did not find item with no quantity in shopping list")

    # remove the recipe one more time and make sure the item is gone and the list is empty
    api_client.post(
        api_routes.households_shopping_lists_item_id_recipe_recipe_id_delete(shopping_list.id, recipe.id),
        headers=unique_user.token,
    )

    response = api_client.get(
        api_routes.households_shopping_lists_item_id(shopping_list.id),
        headers=unique_user.token,
    )
    updated_list = ShoppingListOut.model_validate_json(response.content)
    assert len(updated_list.list_items) == 0


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

    response = api_client.post(api_routes.households_shopping_lists, json=new_list_data, headers=unique_user.token)
    list_as_json = utils.assert_deserialize(response, 201)

    # make sure the extra persists
    extras = list_as_json["extras"]
    assert key_str_1 in extras
    assert extras[key_str_1] == val_str_1

    # add more extras to the list
    list_as_json["extras"][key_str_2] = val_str_2

    response = api_client.put(
        api_routes.households_shopping_lists_item_id(list_as_json["id"]),
        json=list_as_json,
        headers=unique_user.token,
    )
    list_as_json = utils.assert_deserialize(response, 200)

    # make sure both the new extra and original extra persist
    extras = list_as_json["extras"]
    assert key_str_1 in extras
    assert key_str_2 in extras
    assert extras[key_str_1] == val_str_1
    assert extras[key_str_2] == val_str_2


def test_modify_shopping_list_items_updates_shopping_list(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    shopping_list = random.choice(shopping_lists)
    last_update_at = shopping_list.updated_at
    assert last_update_at

    # Create
    new_item_data = {"note": random_string(), "shopping_list_id": str(shopping_list.id)}
    response = api_client.post(api_routes.households_shopping_items, json=new_item_data, headers=unique_user.token)
    data = assert_deserialize(response, 201)
    updated_list = ShoppingListOut.model_validate_json(
        api_client.get(
            api_routes.households_shopping_lists_item_id(shopping_list.id), headers=unique_user.token
        ).content
    )
    assert updated_list and updated_list.updated_at
    assert updated_list.updated_at > last_update_at
    last_update_at = updated_list.updated_at

    list_item_id = data["createdItems"][0]["id"]
    list_item = ShoppingListItemOut.model_validate_json(
        api_client.get(api_routes.households_shopping_items_item_id(list_item_id), headers=unique_user.token).content
    )
    assert list_item

    # Update
    list_item.note = random_string()
    response = api_client.put(
        api_routes.households_shopping_items_item_id(list_item_id),
        json=utils.jsonify(list_item.cast(ShoppingListItemUpdate).model_dump()),
        headers=unique_user.token,
    )
    assert response.status_code == 200
    updated_list = ShoppingListOut.model_validate_json(
        api_client.get(
            api_routes.households_shopping_lists_item_id(shopping_list.id), headers=unique_user.token
        ).content
    )
    assert updated_list and updated_list.updated_at
    assert updated_list.updated_at > last_update_at
    last_update_at = updated_list.updated_at

    # Delete
    response = api_client.delete(
        api_routes.households_shopping_items_item_id(list_item_id),
        headers=unique_user.token,
    )
    assert response.status_code == 200
    updated_list = ShoppingListOut.model_validate_json(
        api_client.get(
            api_routes.households_shopping_lists_item_id(shopping_list.id), headers=unique_user.token
        ).content
    )
    assert updated_list and updated_list.updated_at
    assert updated_list.updated_at > last_update_at


def test_bulk_modify_shopping_list_items_updates_shopping_list(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    shopping_list = random.choice(shopping_lists)
    last_update_at = shopping_list.updated_at
    assert last_update_at

    # Create
    new_item_data = [
        {"note": random_string(), "shopping_list_id": str(shopping_list.id)} for _ in range(random_int(3, 5))
    ]
    response = api_client.post(
        api_routes.households_shopping_items_create_bulk,
        json=new_item_data,
        headers=unique_user.token,
    )
    data = assert_deserialize(response, 201)
    updated_list = ShoppingListOut.model_validate_json(
        api_client.get(
            api_routes.households_shopping_lists_item_id(shopping_list.id), headers=unique_user.token
        ).content
    )
    assert updated_list and updated_list.updated_at
    assert updated_list.updated_at > last_update_at
    last_update_at = updated_list.updated_at

    # Update
    list_item_ids = [item["id"] for item in data["createdItems"]]
    list_items: list[ShoppingListItemOut] = []
    for list_item_id in list_item_ids:
        list_item = ShoppingListItemOut.model_validate_json(
            api_client.get(
                api_routes.households_shopping_items_item_id(list_item_id), headers=unique_user.token
            ).content
        )
        assert list_item
        assert list_item
        list_item.note = random_string()
        list_items.append(list_item)

    payload = [utils.jsonify(list_item.cast(ShoppingListItemUpdateBulk).model_dump()) for list_item in list_items]
    response = api_client.put(api_routes.households_shopping_items, json=payload, headers=unique_user.token)
    assert response.status_code == 200
    updated_list = ShoppingListOut.model_validate_json(
        api_client.get(
            api_routes.households_shopping_lists_item_id(shopping_list.id), headers=unique_user.token
        ).content
    )
    assert updated_list and updated_list.updated_at
    assert updated_list.updated_at > last_update_at
    last_update_at = updated_list.updated_at

    # Delete
    response = api_client.delete(
        api_routes.households_shopping_items,
        params={"ids": [str(list_item.id) for list_item in list_items]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    updated_list = ShoppingListOut.model_validate_json(
        api_client.get(
            api_routes.households_shopping_lists_item_id(shopping_list.id), headers=unique_user.token
        ).content
    )
    assert updated_list and updated_list.updated_at
    assert updated_list.updated_at > last_update_at
