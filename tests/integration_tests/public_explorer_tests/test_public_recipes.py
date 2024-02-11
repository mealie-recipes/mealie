import random
from dataclasses import dataclass
from typing import Any

import pytest
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


@dataclass(slots=True)
class PublicRecipeTestCase:
    private_group: bool
    public_recipe: bool
    status_code: int
    error: str | None


@pytest.mark.parametrize("is_private_group", [True, False], ids=["group_is_private", "group_is_public"])
def test_get_all_public_recipes(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    is_private_group: bool,
):
    ## Set Up Public and Private Recipes
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    group.preferences.recipe_public = not is_private_group
    database.group_preferences.update(group.id, group.preferences)

    default_recipes = database.recipes.create_many(
        [
            Recipe(
                user_id=unique_user.user_id,
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
    response = api_client.get(api_routes.explore_recipes_group_slug(group.slug))
    if is_private_group:
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
    database: AllRepositories,
    query_filter: str,
    recipe_data: dict[str, Any],
    should_fetch: bool,
):
    ## Set Up Recipe
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = False
    group.preferences.recipe_public = True
    database.group_preferences.update(group.id, group.preferences)

    assert random_recipe.settings
    random_recipe.settings.public = True
    database.recipes.update(random_recipe.slug, random_recipe.model_dump() | recipe_data)

    ## Query All Recipes
    response = api_client.get(api_routes.explore_recipes_group_slug(group.slug), params={"queryFilter": query_filter})
    assert response.status_code == 200
    recipes_data = response.json()
    fetched_ids: set[str] = {recipe["id"] for recipe in recipes_data["items"]}
    assert should_fetch is (str(random_recipe.id) in fetched_ids)


@pytest.mark.parametrize(
    "test_case",
    (
        PublicRecipeTestCase(private_group=False, public_recipe=True, status_code=200, error=None),
        PublicRecipeTestCase(private_group=True, public_recipe=True, status_code=404, error="group not found"),
        PublicRecipeTestCase(private_group=False, public_recipe=False, status_code=404, error="recipe not found"),
    ),
    ids=("is public", "group private", "recipe private"),
)
def test_public_recipe_success(
    api_client: TestClient,
    unique_user: TestUser,
    random_recipe: Recipe,
    database: AllRepositories,
    test_case: PublicRecipeTestCase,
):
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = test_case.private_group
    group.preferences.recipe_public = not test_case.private_group
    database.group_preferences.update(group.id, group.preferences)

    # Set Recipe `settings.public` attribute
    assert random_recipe.settings
    random_recipe.settings.public = test_case.public_recipe
    database.recipes.update(random_recipe.slug, random_recipe)

    # Try to access recipe
    recipe_group = database.groups.get_by_slug_or_id(random_recipe.group_id)
    assert recipe_group
    response = api_client.get(
        api_routes.explore_recipes_group_slug_recipe_slug(
            recipe_group.slug,
            random_recipe.slug,
        )
    )
    assert response.status_code == test_case.status_code

    if test_case.error:
        assert response.json()["detail"] == test_case.error
        return

    as_json = response.json()
    assert as_json["name"] == random_recipe.name
    assert as_json["slug"] == random_recipe.slug
