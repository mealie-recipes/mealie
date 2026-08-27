"""
Integration tests for:
- recipe_count field on GET /foods
- GET /foods/empty
- PUT /foods/merge
"""

from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _create_food(api_client: TestClient, user: TestUser) -> dict:
    data = CreateIngredientFood(name=random_string(10)).model_dump(by_alias=True)
    response = api_client.post(api_routes.foods, json=data, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _create_recipe(api_client: TestClient, user: TestUser) -> str:
    """Creates a recipe and returns its slug."""
    response = api_client.post(api_routes.recipes, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _set_recipe_foods(api_client: TestClient, user: TestUser, slug: str, foods: list[dict]) -> None:
    response = api_client.get(api_routes.recipes_slug(slug), headers=user.token)
    assert response.status_code == 200
    body = response.json()
    body["recipeIngredient"] = [{"quantity": 1, "food": food, "unit": None, "note": ""} for food in foods]
    response = api_client.put(api_routes.recipes_slug(slug), json=body, headers=user.token)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Foods — recipe_count
# ---------------------------------------------------------------------------


def test_food_list_includes_recipe_count_for_used_food(api_client: TestClient, unique_user: TestUser):
    food = _create_food(api_client, unique_user)
    slug = _create_recipe(api_client, unique_user)
    _set_recipe_foods(api_client, unique_user, slug, [food])

    response = api_client.get(api_routes.foods, headers=unique_user.token)
    assert response.status_code == 200
    items = response.json()["items"]
    match = next((f for f in items if f["id"] == food["id"]), None)
    assert match is not None
    assert match["recipeCount"] == 1

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.foods_item_id(food["id"]), headers=unique_user.token)


def test_food_list_recipe_count_is_zero_for_unused_food(api_client: TestClient, unique_user: TestUser):
    food = _create_food(api_client, unique_user)

    response = api_client.get(api_routes.foods, headers=unique_user.token)
    assert response.status_code == 200
    items = response.json()["items"]
    match = next((f for f in items if f["id"] == food["id"]), None)
    assert match is not None
    assert match["recipeCount"] == 0

    api_client.delete(api_routes.foods_item_id(food["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Foods — empty
# ---------------------------------------------------------------------------


def test_foods_empty_includes_unused_food_and_excludes_used_food(api_client: TestClient, unique_user: TestUser):
    unused_food = _create_food(api_client, unique_user)
    used_food = _create_food(api_client, unique_user)
    slug = _create_recipe(api_client, unique_user)
    _set_recipe_foods(api_client, unique_user, slug, [used_food])

    response = api_client.get(api_routes.foods_empty, headers=unique_user.token)
    assert response.status_code == 200
    ids = [f["id"] for f in response.json()]
    assert unused_food["id"] in ids
    assert used_food["id"] not in ids

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.foods_item_id(unused_food["id"]), headers=unique_user.token)
    api_client.delete(api_routes.foods_item_id(used_food["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Foods — merge
# ---------------------------------------------------------------------------


def test_food_merge_moves_ingredients_to_target(api_client: TestClient, unique_user: TestUser):
    from_food = _create_food(api_client, unique_user)
    to_food = _create_food(api_client, unique_user)

    slug1 = _create_recipe(api_client, unique_user)
    slug2 = _create_recipe(api_client, unique_user)
    _set_recipe_foods(api_client, unique_user, slug1, [from_food])
    _set_recipe_foods(api_client, unique_user, slug2, [to_food])

    response = api_client.put(
        api_routes.foods_merge,
        json={"fromFood": from_food["id"], "toFood": to_food["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200

    # from_food must be deleted
    assert api_client.get(api_routes.foods_item_id(from_food["id"]), headers=unique_user.token).status_code == 404

    to_food_after = api_client.get(api_routes.foods_item_id(to_food["id"]), headers=unique_user.token).json()
    assert to_food_after["recipeCount"] == 2

    for slug in (slug1, slug2):
        recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
        food_ids = [ing["food"]["id"] for ing in recipe["recipeIngredient"]]
        assert to_food["id"] in food_ids
        assert from_food["id"] not in food_ids

    api_client.delete(api_routes.recipes_slug(slug1), headers=unique_user.token)
    api_client.delete(api_routes.recipes_slug(slug2), headers=unique_user.token)
    api_client.delete(api_routes.foods_item_id(to_food["id"]), headers=unique_user.token)
