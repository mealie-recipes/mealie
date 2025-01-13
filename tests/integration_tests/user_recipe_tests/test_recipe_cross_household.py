from datetime import UTC, datetime, timedelta

import pytest
from dateutil.parser import parse as parse_dt
from fastapi.testclient import TestClient

from mealie.schema.cookbook.cookbook import SaveCookBook
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_category import TagSave
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
def test_get_all_recipes_with_household_filter(
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

    response = api_client.get(
        api_routes.recipes,
        params={"households": [h2_recipe.household_id], "page": 1, "perPage": -1},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    response_ids = {recipe["id"] for recipe in response.json()["items"]}
    assert str(recipe_id) not in response_ids
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
@pytest.mark.parametrize("household_lock_recipe_edits", [True, False])
@pytest.mark.parametrize("use_patch", [True, False])
def test_update_recipes_in_other_households(
    api_client: TestClient,
    unique_user: TestUser,
    h2_user: TestUser,
    is_private_household: bool,
    household_lock_recipe_edits: bool,
    use_patch: bool,
):
    household = unique_user.repos.households.get_one(h2_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = is_private_household
    household.preferences.lock_recipe_edits_from_other_households = household_lock_recipe_edits
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
    response = client_func(api_routes.recipes_slug(recipe["id"]), json=recipe, headers=unique_user.token)

    if household_lock_recipe_edits:
        assert response.status_code == 403

        # confirm the recipe is unchanged
        response = api_client.get(api_routes.recipes_slug(recipe["id"]), headers=unique_user.token)
        assert response.status_code == 200
        updated_recipe = response.json()
        assert updated_recipe["name"] == original_name != updated_name
    else:
        assert response.status_code == 200

        # confirm the recipe was updated
        response = api_client.get(api_routes.recipes_slug(recipe["id"]), headers=unique_user.token)
        assert response.status_code == 200
        updated_recipe = response.json()
        assert updated_recipe["name"] == updated_name != original_name


@pytest.mark.parametrize("is_private_household", [True, False])
@pytest.mark.parametrize("household_lock_recipe_edits", [True, False])
def test_delete_recipes_from_other_households(
    api_client: TestClient,
    unique_user: TestUser,
    h2_user: TestUser,
    is_private_household: bool,
    household_lock_recipe_edits: bool,
):
    household = unique_user.repos.households.get_one(h2_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = is_private_household
    household.preferences.lock_recipe_edits_from_other_households = household_lock_recipe_edits
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
    if household_lock_recipe_edits:
        assert response.status_code == 403

        # confirm the recipe still exists
        response = api_client.get(api_routes.recipes_slug(h2_recipe_id), headers=unique_user.token)
        assert response.status_code == 200
        assert response.json()["id"] == h2_recipe_id
    else:
        assert response.status_code == 200

        # confirm the recipe was deleted
        response = api_client.get(api_routes.recipes_slug(h2_recipe_id), headers=unique_user.token)
        assert response.status_code == 404


@pytest.mark.parametrize("is_private_household", [True, False])
@pytest.mark.parametrize("household_lock_recipe_edits", [True, False])
def test_user_can_update_last_made_on_other_household(
    api_client: TestClient,
    unique_user: TestUser,
    h2_user: TestUser,
    is_private_household: bool,
    household_lock_recipe_edits: bool,
):
    household = unique_user.repos.households.get_one(h2_user.household_id)
    assert household and household.preferences
    household.preferences.private_household = is_private_household
    household.preferences.lock_recipe_edits_from_other_households = household_lock_recipe_edits
    unique_user.repos.household_preferences.update(household.id, household.preferences)

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=h2_user.token)
    assert response.status_code == 201
    h2_recipe = h2_user.repos.recipes.get_one(response.json())
    assert h2_recipe and h2_recipe.id
    h2_recipe_slug = h2_recipe.slug

    dt_1 = datetime.now(tz=UTC)
    dt_2 = dt_1 + timedelta(days=2)

    # set last made for unique_user and make sure it only updates globally and for unique_user
    response = api_client.patch(
        api_routes.recipes_slug_last_made(h2_recipe.slug),
        json={"timestamp": dt_2.isoformat()},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    response = api_client.get(api_routes.households_self_recipes_recipe_slug(h2_recipe_slug), headers=unique_user.token)
    assert response.status_code == 200
    assert (last_made_json := response.json()["lastMade"])
    assert parse_dt(last_made_json) == dt_2

    response = api_client.get(api_routes.households_self_recipes_recipe_slug(h2_recipe_slug), headers=h2_user.token)
    assert response.status_code == 200
    assert response.json()["lastMade"] is None

    recipe = h2_user.repos.recipes.get_one(h2_recipe_slug)
    assert recipe
    assert recipe.last_made == dt_2

    # set last made for h2_user and make sure it only updates globally and for h2_user
    response = api_client.patch(
        api_routes.recipes_slug_last_made(h2_recipe.slug), json={"timestamp": dt_1.isoformat()}, headers=h2_user.token
    )
    assert response.status_code == 200
    response = api_client.get(api_routes.households_self_recipes_recipe_slug(h2_recipe_slug), headers=h2_user.token)
    assert response.status_code == 200
    assert (last_made_json := response.json()["lastMade"])
    assert parse_dt(last_made_json) == dt_1

    response = api_client.get(api_routes.households_self_recipes_recipe_slug(h2_recipe_slug), headers=unique_user.token)
    assert response.status_code == 200
    assert (last_made_json := response.json()["lastMade"])
    assert parse_dt(last_made_json) == dt_2

    # this shouldn't have updated since dt_2 is newer than dt_1
    recipe = h2_user.repos.recipes.get_one(h2_recipe_slug)
    assert recipe
    assert recipe.last_made == dt_2


def test_cookbook_recipes_includes_all_households(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    tag = unique_user.repos.tags.create(TagSave(name=random_string(), group_id=unique_user.group_id))
    recipes = unique_user.repos.recipes.create_many(
        [
            Recipe(
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                name=random_string(),
                tags=[tag],
            )
            for _ in range(3)
        ]
    )
    other_recipes = h2_user.repos.recipes.create_many(
        [
            Recipe(
                user_id=h2_user.user_id,
                group_id=h2_user.group_id,
                name=random_string(),
            )
            for _ in range(3)
        ]
    )

    cookbook = unique_user.repos.cookbooks.create(
        SaveCookBook(
            name=random_string(),
            group_id=unique_user.group_id,
            household_id=unique_user.household_id,
            tags=[tag],
        )
    )

    response = api_client.get(api_routes.recipes, params={"cookbook": cookbook.slug}, headers=unique_user.token)
    assert response.status_code == 200
    recipes = [Recipe.model_validate(data) for data in response.json()["items"]]

    fetched_recipe_ids = {recipe.id for recipe in recipes}
    for recipe in recipes:
        assert recipe.id in fetched_recipe_ids
    for recipe in other_recipes:
        assert recipe.id in fetched_recipe_ids


def test_cookbooks_from_other_households(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    h2_cookbook = h2_user.repos.cookbooks.create(
        SaveCookBook(
            name=random_string(),
            group_id=h2_user.group_id,
            household_id=h2_user.household_id,
        )
    )

    response = api_client.get(api_routes.recipes, params={"cookbook": h2_cookbook.slug}, headers=unique_user.token)
    assert response.status_code == 200
