from fastapi.testclient import TestClient

from mealie.schema.cookbook import CookBookSave
from mealie.schema.recipe.recipe import RecipeDraft
from mealie.schema.recipe.recipe_ingredient import (
    IngredientFoodSave,
    RecipeIngredient,
)
from mealie.schema.recipe.recipe_settings import RecipeSettings
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _create_recipe(user: TestUser, food_id: str, name: str | None = None):
    food_obj = user.repos.ingredient_foods.get_one(food_id)
    assert food_obj is not None
    return user.repos.recipes.create(
        RecipeDraft(
            user_id=user.user_id,
            group_id=user.group_id,
            name=name or random_string(),
            recipe_ingredient=[RecipeIngredient(food_id=food_id, food=food_obj)],
            settings=RecipeSettings(),
        )
    )


def test_food_hierarchy_api_crud_and_validation(api_client: TestClient, unique_user: TestUser, g2_user: TestUser):
    # 1. Create parent food
    parent_resp = api_client.post(
        api_routes.foods,
        json={"name": f"Parent_{random_string(6)}", "description": "Parent category"},
        headers=unique_user.token,
    )
    assert parent_resp.status_code == 201
    parent_food = parent_resp.json()
    assert parent_food["parentId"] is None
    assert parent_food["parent"] is None

    # 2. Create child food referencing parent
    child_resp = api_client.post(
        api_routes.foods,
        json={
            "name": f"Child_{random_string(6)}",
            "parentId": parent_food["id"],
        },
        headers=unique_user.token,
    )
    assert child_resp.status_code == 201
    child_food = child_resp.json()
    assert child_food["parentId"] == parent_food["id"]
    assert child_food["parent"] is not None
    assert child_food["parent"]["id"] == parent_food["id"]

    # 3. Read child food via GET
    get_child = api_client.get(api_routes.foods_item_id(child_food["id"]), headers=unique_user.token)
    assert get_child.status_code == 200
    assert get_child.json()["parentId"] == parent_food["id"]
    assert get_child.json()["parent"]["name"] == parent_food["name"]

    # 4. Update child food: clear parent
    update_resp = api_client.put(
        api_routes.foods_item_id(child_food["id"]),
        json={"id": child_food["id"], "name": child_food["name"], "parentId": None},
        headers=unique_user.token,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["parentId"] is None
    assert update_resp.json()["parent"] is None

    # Re-attach parent
    api_client.put(
        api_routes.foods_item_id(child_food["id"]),
        json={"id": child_food["id"], "name": child_food["name"], "parentId": parent_food["id"]},
        headers=unique_user.token,
    )

    # 5. Validation: self-parenting
    self_resp = api_client.put(
        api_routes.foods_item_id(child_food["id"]),
        json={"id": child_food["id"], "name": child_food["name"], "parentId": child_food["id"]},
        headers=unique_user.token,
    )
    assert self_resp.status_code in (400, 422)

    # 6. Validation: 3-level depth (cannot set parent to a food that already has a parent)
    grandchild_resp = api_client.post(
        api_routes.foods,
        json={"name": f"Grandchild_{random_string(6)}", "parentId": child_food["id"]},
        headers=unique_user.token,
    )
    assert grandchild_resp.status_code in (400, 422)

    # 7. Validation: 3-level depth (cannot set parent on a food that already has children)
    other_parent = api_client.post(
        api_routes.foods,
        json={"name": f"OtherParent_{random_string(6)}"},
        headers=unique_user.token,
    ).json()

    parent_with_child_resp = api_client.put(
        api_routes.foods_item_id(parent_food["id"]),
        json={"id": parent_food["id"], "name": parent_food["name"], "parentId": other_parent["id"]},
        headers=unique_user.token,
    )
    assert parent_with_child_resp.status_code in (400, 422)

    # 8. Validation: cross-group isolation
    g2_food = g2_user.repos.ingredient_foods.create(
        IngredientFoodSave(
            name=f"G2Food_{random_string(6)}",
            group_id=g2_user.group_id,
        )
    )

    cross_group_resp = api_client.post(
        api_routes.foods,
        json={"name": f"CrossGroup_{random_string(6)}", "parentId": str(g2_food.id)},
        headers=unique_user.token,
    )
    assert cross_group_resp.status_code in (400, 422)


def test_recipe_filtering_expands_to_child_foods(api_client: TestClient, unique_user: TestUser):
    # Create Mushroom (parent)
    mushroom = api_client.post(
        api_routes.foods,
        json={"name": f"Mushroom_{random_string(6)}"},
        headers=unique_user.token,
    ).json()

    # Create Porcini (child of Mushroom)
    porcini = api_client.post(
        api_routes.foods,
        json={"name": f"Porcini_{random_string(6)}", "parentId": mushroom["id"]},
        headers=unique_user.token,
    ).json()

    # Create Champignon (child of Mushroom)
    champignon = api_client.post(
        api_routes.foods,
        json={"name": f"Champignon_{random_string(6)}", "parentId": mushroom["id"]},
        headers=unique_user.token,
    ).json()

    # Create Tomato (unrelated food)
    tomato = api_client.post(
        api_routes.foods,
        json={"name": f"Tomato_{random_string(6)}"},
        headers=unique_user.token,
    ).json()

    # Create recipes
    recipe_mushroom = _create_recipe(unique_user, mushroom["id"], name=f"Mushroom Soup {random_string(4)}")
    recipe_porcini = _create_recipe(unique_user, porcini["id"], name=f"Risotto {random_string(4)}")
    recipe_champignon = _create_recipe(unique_user, champignon["id"], name=f"Pizza {random_string(4)}")
    recipe_tomato = _create_recipe(unique_user, tomato["id"], name=f"Pasta {random_string(4)}")

    # Query recipes filtering by Mushroom (parent): MUST return Mushroom, Porcini and Champignon recipes, but not Tomato
    resp = api_client.get(
        api_routes.recipes,
        params={"foods": [mushroom["id"]]},
        headers=unique_user.token,
    )
    assert resp.status_code == 200
    returned_ids = [r["id"] for r in resp.json()["items"]]
    assert str(recipe_mushroom.id) in returned_ids
    assert str(recipe_porcini.id) in returned_ids
    assert str(recipe_champignon.id) in returned_ids
    assert str(recipe_tomato.id) not in returned_ids

    # Query recipes filtering by Mushroom with expandFoods=False (used by delete warning):
    # MUST return only recipes using Mushroom directly, NOT children
    resp_exact = api_client.get(
        api_routes.recipes,
        params={"foods": [mushroom["id"]], "expandFoods": False},
        headers=unique_user.token,
    )
    assert resp_exact.status_code == 200
    exact_ids = [r["id"] for r in resp_exact.json()["items"]]
    assert str(recipe_mushroom.id) in exact_ids
    assert str(recipe_porcini.id) not in exact_ids
    assert str(recipe_champignon.id) not in exact_ids

    # Query recipes filtering by Porcini (child): MUST return only Porcini recipe
    resp_porcini = api_client.get(
        api_routes.recipes,
        params={"foods": [porcini["id"]]},
        headers=unique_user.token,
    )
    assert resp_porcini.status_code == 200
    porcini_ids = [r["id"] for r in resp_porcini.json()["items"]]
    assert str(recipe_porcini.id) in porcini_ids
    assert str(recipe_champignon.id) not in porcini_ids
    assert str(recipe_tomato.id) not in porcini_ids

    # Query recipes filtering by Tomato: MUST return only Tomato recipe
    resp_tomato = api_client.get(
        api_routes.recipes,
        params={"foods": [tomato["id"]]},
        headers=unique_user.token,
    )
    assert resp_tomato.status_code == 200
    tomato_ids = [r["id"] for r in resp_tomato.json()["items"]]
    assert str(recipe_tomato.id) in tomato_ids
    assert str(recipe_porcini.id) not in tomato_ids
    assert str(recipe_champignon.id) not in tomato_ids


def test_cookbook_query_filter_expands_to_child_foods(api_client: TestClient, unique_user: TestUser):
    # Create Mushroom (parent)
    mushroom = api_client.post(
        api_routes.foods,
        json={"name": f"ParentFood_{random_string(6)}"},
        headers=unique_user.token,
    ).json()

    # Create Porcini (child)
    porcini = api_client.post(
        api_routes.foods,
        json={"name": f"ChildFood_{random_string(6)}", "parentId": mushroom["id"]},
        headers=unique_user.token,
    ).json()

    # Create Tomato (unrelated)
    tomato = api_client.post(
        api_routes.foods,
        json={"name": f"OtherFood_{random_string(6)}"},
        headers=unique_user.token,
    ).json()

    recipe_child = _create_recipe(unique_user, porcini["id"])
    recipe_other = _create_recipe(unique_user, tomato["id"])

    # Create cookbook with query filter on parent food ID
    cb = unique_user.repos.cookbooks.create(
        CookBookSave(
            name=f"Cookbook_{random_string(6)}",
            group_id=unique_user.group_id,
            household_id=unique_user.household_id,
            query_filter_string=f'recipe_ingredient.food.id IN ["{mushroom["id"]}"]',
        )
    )

    resp = api_client.get(
        api_routes.recipes,
        params={"cookbook": str(cb.id)},
        headers=unique_user.token,
    )
    assert resp.status_code == 200
    cb_recipe_ids = [r["id"] for r in resp.json()["items"]]
    assert str(recipe_child.id) in cb_recipe_ids
    assert str(recipe_other.id) not in cb_recipe_ids


def test_food_hierarchy_delete_sets_child_parent_none(api_client: TestClient, unique_user: TestUser):
    parent = api_client.post(
        api_routes.foods,
        json={"name": f"ToDeleteParent_{random_string(6)}"},
        headers=unique_user.token,
    ).json()

    child = api_client.post(
        api_routes.foods,
        json={"name": f"Child_{random_string(6)}", "parentId": parent["id"]},
        headers=unique_user.token,
    ).json()

    # Delete parent
    del_resp = api_client.delete(api_routes.foods_item_id(parent["id"]), headers=unique_user.token)
    assert del_resp.status_code == 200

    # Verify child still exists and parent_id is now None
    child_after = api_client.get(api_routes.foods_item_id(child["id"]), headers=unique_user.token)
    assert child_after.status_code == 200
    assert child_after.json()["parentId"] is None
    assert child_after.json()["parent"] is None


def test_food_hierarchy_merge(api_client: TestClient, unique_user: TestUser):
    # Family 1: P1 -> C1
    p1 = api_client.post(api_routes.foods, json={"name": f"P1_{random_string(6)}"}, headers=unique_user.token).json()
    c1 = api_client.post(
        api_routes.foods, json={"name": f"C1_{random_string(6)}", "parentId": p1["id"]}, headers=unique_user.token
    ).json()

    # Family 2: P2 -> C2
    p2 = api_client.post(api_routes.foods, json={"name": f"P2_{random_string(6)}"}, headers=unique_user.token).json()
    api_client.post(
        api_routes.foods, json={"name": f"C2_{random_string(6)}", "parentId": p2["id"]}, headers=unique_user.token
    )

    # Merge P1 into P2: C1 should now have parent P2
    merge_resp = api_client.put(
        api_routes.foods + "/merge",
        json={"from_food": p1["id"], "to_food": p2["id"]},
        headers=unique_user.token,
    )
    assert merge_resp.status_code == 200

    c1_after = api_client.get(api_routes.foods_item_id(c1["id"]), headers=unique_user.token).json()
    assert c1_after["parentId"] == p2["id"]
