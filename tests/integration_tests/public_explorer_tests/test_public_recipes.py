import random
from typing import Any

import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import Recipe
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("is_private_group", [True, False])
@pytest.mark.parametrize("is_private_household", [True, False])
def test_get_all_public_recipes(
    api_client: TestClient,
    unique_user: TestUser,
    is_private_group: bool,
    is_private_household: bool,
):
    database = unique_user.repos

    ## Set Up Public and Private Recipes
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    database.group_preferences.update(group.id, group.preferences)

    household = database.households.get_one(unique_user.household_id)
    assert household and household.preferences

    household.preferences.private_household = is_private_household
    household.preferences.recipe_public = not is_private_household
    database.household_preferences.update(household.id, household.preferences)

    default_recipes = database.recipes.create_many(
        [
            Recipe(
                user_id=unique_user.user_id,
                household_id=unique_user.household_id,
                group_id=unique_user.group_id,
                name=random_string(),
            )
            for _ in range(random_int(15, 20))
        ],
    )

    random.shuffle(default_recipes)
    split_index = random_int(6, 12)
    public_recipes = default_recipes[:split_index]
    private_recipes = default_recipes[split_index:]

    for recipe in public_recipes:
        assert recipe.settings
        recipe.settings.public = True

    for recipe in private_recipes:
        assert recipe.settings
        recipe.settings.public = False

    database.recipes.update_many(public_recipes + private_recipes)

    ## Query All Recipes
    response = api_client.get(
        api_routes.explore_groups_group_slug_households_household_slug_recipes(group.slug, household.slug)
    )
    if is_private_group or is_private_household:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    recipes_data = response.json()
    fetched_ids: set[str] = {recipe["id"] for recipe in recipes_data["items"]}

    for recipe in public_recipes:
        assert str(recipe.id) in fetched_ids

    for recipe in private_recipes:
        assert str(recipe.id) not in fetched_ids


@pytest.mark.parametrize(
    "query_filter, recipe_data, should_fetch",
    [
        ('slug = "mypublicslug"', {"slug": "mypublicslug"}, True),
        ('slug = "mypublicslug"', {"slug": "notmypublicslug"}, False),
        ("settings.public = FALSE", {}, False),
        ("settings.public <> TRUE", {}, False),
    ],
    ids=[
        "match_slug",
        "not_match_slug",
        "bypass_public_filter_1",
        "bypass_public_filter_2",
    ],
)
def test_get_all_public_recipes_filtered(
    api_client: TestClient,
    unique_user: TestUser,
    random_recipe: Recipe,
    query_filter: str,
    recipe_data: dict[str, Any],
    should_fetch: bool,
):
    database = unique_user.repos

    ## Set Up Recipe
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = False
    database.group_preferences.update(group.id, group.preferences)

    household = database.households.get_one(unique_user.household_id)
    assert household and household.preferences

    household.preferences.private_household = False
    household.preferences.recipe_public = True
    database.household_preferences.update(household.id, household.preferences)

    assert random_recipe.settings
    random_recipe.settings.public = True
    database.recipes.update(random_recipe.slug, random_recipe.model_dump() | recipe_data)

    ## Query All Recipes
    response = api_client.get(
        api_routes.explore_groups_group_slug_households_household_slug_recipes(group.slug, household.slug),
        params={"queryFilter": query_filter},
    )
    assert response.status_code == 200
    recipes_data = response.json()
    fetched_ids: set[str] = {recipe["id"] for recipe in recipes_data["items"]}
    assert should_fetch is (str(random_recipe.id) in fetched_ids)


@pytest.mark.parametrize("is_private_group", [True, False])
@pytest.mark.parametrize("is_private_household", [True, False])
@pytest.mark.parametrize("is_private_recipe", [True, False])
def test_public_recipe_success(
    api_client: TestClient,
    unique_user: TestUser,
    random_recipe: Recipe,
    is_private_group: bool,
    is_private_household: bool,
    is_private_recipe: bool,
):
    database = unique_user.repos

    ## Set Up Group
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    database.group_preferences.update(group.id, group.preferences)

    ## Set Up Household
    household = database.households.get_one(unique_user.household_id)
    assert household and household.preferences

    household.preferences.private_household = is_private_household
    household.preferences.recipe_public = not is_private_household
    database.household_preferences.update(household.id, household.preferences)

    # Set Recipe `settings.public` attribute
    assert random_recipe.settings
    random_recipe.settings.public = not is_private_recipe
    database.recipes.update(random_recipe.slug, random_recipe)

    # Try to access recipe
    recipe_group = database.groups.get_by_slug_or_id(random_recipe.group_id)
    recipe_household = database.households.get_by_slug_or_id(random_recipe.household_id)
    assert recipe_group
    assert recipe_household
    response = api_client.get(
        api_routes.explore_groups_group_slug_households_household_slug_recipes_recipe_slug(
            recipe_group.slug,
            recipe_household.slug,
            random_recipe.slug,
        )
    )
    if is_private_group or is_private_household or is_private_recipe:
        assert response.status_code == 404
        if is_private_group:
            assert response.json()["detail"] == "group not found"
        elif is_private_household:
            assert response.json()["detail"] == "household not found"
        else:
            assert response.json()["detail"] == "recipe not found"

        return

    as_json = response.json()
    assert as_json["name"] == random_recipe.name
    assert as_json["slug"] == random_recipe.slug
