from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("is_private_household", [True, False])
def test_duplicate_recipe_changes_household(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser, is_private_household: bool
):
    household = unique_user.repos.households.get_one(h2_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = is_private_household
    unique_user.repos.household_preferences.update(household.id, household.preferences)

    source_recipe_name = random_string()
    duplicate_recipe_name = random_string()

    response = api_client.post(api_routes.recipes, json={"name": source_recipe_name}, headers=unique_user.token)
    assert response.status_code == 201
    recipe = unique_user.repos.recipes.get_one(response.json())
    assert recipe
    assert recipe.name == source_recipe_name
    assert str(recipe.household_id) == unique_user.household_id

    response = api_client.post(
        api_routes.recipes_slug_duplicate(recipe.slug), json={"name": duplicate_recipe_name}, headers=h2_user.token
    )
    assert response.status_code == 201
    duplicate_recipe = h2_user.repos.recipes.get_one(response.json()["slug"])
    assert duplicate_recipe
    assert duplicate_recipe.name == duplicate_recipe_name
    assert str(duplicate_recipe.household_id) == h2_user.household_id != unique_user.household_id


@pytest.mark.parametrize("is_private_household", [True, False])
def test_get_all_recipes_includes_all_households(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser, is_private_household: bool
):
    household = unique_user.repos.households.get_one(h2_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = is_private_household
    unique_user.repos.household_preferences.update(household.id, household.preferences)

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=unique_user.token)
    assert response.status_code == 201
    recipe = unique_user.repos.recipes.get_one(response.json())
    assert recipe and recipe.id
    recipe_id = recipe.id

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=h2_user.token)
    assert response.status_code == 201
    h2_recipe = h2_user.repos.recipes.get_one(response.json())
    assert h2_recipe and h2_recipe.id
    h2_recipe_id = h2_recipe.id

    response = api_client.get(api_routes.recipes, params={"page": 1, "perPage": -1}, headers=unique_user.token)
    assert response.status_code == 200
    response_ids = {recipe["id"] for recipe in response.json()["items"]}
    assert str(recipe_id) in response_ids
    assert str(h2_recipe_id) in response_ids


@pytest.mark.parametrize("is_private_household", [True, False])
def test_get_one_recipe_from_another_household(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser, is_private_household: bool
):
    household = unique_user.repos.households.get_one(h2_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = is_private_household
    unique_user.repos.household_preferences.update(household.id, household.preferences)

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=h2_user.token)
    assert response.status_code == 201
    h2_recipe = h2_user.repos.recipes.get_one(response.json())
    assert h2_recipe and h2_recipe.id
    h2_recipe_id = h2_recipe.id

    response = api_client.get(api_routes.recipes_slug(h2_recipe_id), headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["id"] == str(h2_recipe_id)


@pytest.mark.parametrize("is_private_household", [True, False])
@pytest.mark.parametrize("use_patch", [True, False])
def test_prevent_updates_to_recipes_from_other_households(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser, is_private_household: bool, use_patch: bool
):
    household = unique_user.repos.households.get_one(h2_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = is_private_household
    unique_user.repos.household_preferences.update(household.id, household.preferences)

    original_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": original_name}, headers=h2_user.token)
    assert response.status_code == 201
    h2_recipe = h2_user.repos.recipes.get_one(response.json())
    assert h2_recipe and h2_recipe.id
    h2_recipe_id = h2_recipe.id

    response = api_client.get(api_routes.recipes_slug(h2_recipe_id), headers=unique_user.token)
    assert response.status_code == 200
    recipe = response.json()
    assert recipe["id"] == str(h2_recipe_id)

    updated_name = random_string()
    recipe["name"] = updated_name
    client_func = api_client.patch if use_patch else api_client.put
    response = client_func(api_routes.recipes_slug(recipe["slug"]), json=recipe, headers=unique_user.token)
    assert response.status_code == 403

    # confirm the recipe is unchanged
    response = api_client.get(api_routes.recipes_slug(recipe["slug"]), headers=unique_user.token)
    assert response.status_code == 200
    updated_recipe = response.json()
    assert updated_recipe["name"] == original_name != updated_name


@pytest.mark.parametrize("is_private_household", [True, False])
def test_prevent_deletes_to_recipes_from_other_households(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser, is_private_household: bool
):
    household = unique_user.repos.households.get_one(h2_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = is_private_household
    unique_user.repos.household_preferences.update(household.id, household.preferences)

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=h2_user.token)
    assert response.status_code == 201
    h2_recipe = h2_user.repos.recipes.get_one(response.json())
    assert h2_recipe and h2_recipe.id
    h2_recipe_id = str(h2_recipe.id)

    response = api_client.get(api_routes.recipes_slug(h2_recipe_id), headers=unique_user.token)
    assert response.status_code == 200
    recipe_json = response.json()
    assert recipe_json["id"] == h2_recipe_id

    response = api_client.delete(api_routes.recipes_slug(recipe_json["slug"]), headers=unique_user.token)
    assert response.status_code == 403

    # confirm the recipe still exists
    response = api_client.get(api_routes.recipes_slug(h2_recipe_id), headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["id"] == h2_recipe_id


@pytest.mark.parametrize("is_private_household", [True, False])
def test_user_can_update_last_made_on_other_household(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser, is_private_household: bool
):
    household = unique_user.repos.households.get_one(h2_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = is_private_household
    unique_user.repos.household_preferences.update(household.id, household.preferences)

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=h2_user.token)
    assert response.status_code == 201
    h2_recipe = h2_user.repos.recipes.get_one(response.json())
    assert h2_recipe and h2_recipe.id
    h2_recipe_id = h2_recipe.id
    h2_recipe_slug = h2_recipe.slug

    response = api_client.get(api_routes.recipes_slug(h2_recipe_slug), headers=unique_user.token)
    assert response.status_code == 200
    recipe = response.json()
    assert recipe["id"] == str(h2_recipe_id)
    old_last_made = recipe["lastMade"]

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    response = api_client.patch(
        api_routes.recipes_slug_last_made(h2_recipe_slug), json={"timestamp": now}, headers=unique_user.token
    )
    assert response.status_code == 200

    # confirm the last made date was updated
    response = api_client.get(api_routes.recipes_slug(h2_recipe_slug), headers=unique_user.token)
    assert response.status_code == 200
    recipe = response.json()
    assert recipe["id"] == str(h2_recipe_id)
    new_last_made = recipe["lastMade"]
    assert new_last_made == now != old_last_made
