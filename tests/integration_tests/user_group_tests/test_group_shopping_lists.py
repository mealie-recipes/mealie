import random

from fastapi.testclient import TestClient

from mealie.schema.group.group_shopping_list import ShoppingListOut
from mealie.schema.recipe.recipe import Recipe
from tests import utils
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/shopping/lists"

    def item(item_id: str) -> str:
        return f"{Routes.base}/{item_id}"

    def add_recipe(item_id: str, recipe_id: str) -> str:
        return f"{Routes.item(item_id)}/recipe/{recipe_id}"


def test_shopping_lists_get_all(api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]):
    all_lists = api_client.get(Routes.base, headers=unique_user.token)
    assert all_lists.status_code == 200
    all_lists = all_lists.json()

    assert len(all_lists) == len(shopping_lists)

    known_ids = [str(model.id) for model in shopping_lists]

    for list_ in all_lists:
        assert list_["id"] in known_ids


def test_shopping_lists_create_one(api_client: TestClient, unique_user: TestUser):
    payload = {
        "name": random_string(10),
    }

    response = api_client.post(Routes.base, json=payload, headers=unique_user.token)
    response_list = utils.assert_derserialize(response, 201)

    assert response_list["name"] == payload["name"]
    assert response_list["groupId"] == str(unique_user.group_id)


def test_shopping_lists_get_one(api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]):
    shopping_list = shopping_lists[0]

    response = api_client.get(Routes.item(shopping_list.id), headers=unique_user.token)
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

    response = api_client.put(Routes.item(sample_list.id), json=payload, headers=unique_user.token)
    assert response.status_code == 200

    response_list = response.json()

    assert response_list["id"] == str(sample_list.id)
    assert response_list["name"] == payload["name"]
    assert response_list["groupId"] == str(sample_list.group_id)


def test_shopping_lists_delete_one(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    sample_list = random.choice(shopping_lists)

    response = api_client.delete(Routes.item(sample_list.id), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(Routes.item(sample_list.id), headers=unique_user.token)
    assert response.status_code == 404


def test_shopping_lists_add_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)

    recipe = recipe_ingredient_only

    response = api_client.post(Routes.add_recipe(sample_list.id, recipe.id), headers=unique_user.token)
    assert response.status_code == 200

    # Get List and Check for Ingredients

    response = api_client.get(Routes.item(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = [ingredient.note for ingredient in recipe.recipe_ingredient]

    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

    # Check Recipe Reference was added with quantity 1
    refs = item["recipeReferences"]

    assert len(refs) == 1

    assert refs[0]["recipeId"] == recipe.id


def test_shopping_lists_remove_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
    recipe_ingredient_only: Recipe,
):
    sample_list = random.choice(shopping_lists)

    recipe = recipe_ingredient_only

    response = api_client.post(Routes.add_recipe(sample_list.id, recipe.id), headers=unique_user.token)
    assert response.status_code == 200

    # Get List and Check for Ingredients
    response = api_client.get(Routes.item(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = [ingredient.note for ingredient in recipe.recipe_ingredient]

    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

    # Remove Recipe
    response = api_client.delete(Routes.add_recipe(sample_list.id, recipe.id), headers=unique_user.token)

    # Get List and Check for Ingredients
    response = api_client.get(Routes.item(sample_list.id), headers=unique_user.token)
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
        response = api_client.post(Routes.add_recipe(sample_list.id, recipe.id), headers=unique_user.token)
        assert response.status_code == 200

    response = api_client.get(Routes.item(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    known_ingredients = [ingredient.note for ingredient in recipe.recipe_ingredient]

    for item in as_json["listItems"]:
        assert item["note"] in known_ingredients

    # Remove Recipe
    response = api_client.delete(Routes.add_recipe(sample_list.id, recipe.id), headers=unique_user.token)

    # Get List and Check for Ingredients
    response = api_client.get(Routes.item(sample_list.id), headers=unique_user.token)
    as_json = utils.assert_derserialize(response, 200)

    # All Items Should Still Exists
    assert len(as_json["listItems"]) == len(recipe.recipe_ingredient)

    # Quantity Should Equal 2 Start with 3 remove 1)
    for item in as_json["listItems"]:
        assert item["quantity"] == 2.0

    refs = as_json["recipeReferences"]
    assert len(refs) == 1
    assert refs[0]["recipeId"] == recipe.id
