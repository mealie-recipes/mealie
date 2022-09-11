from collections.abc import Generator
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe
from tests.utils import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/explore/recipes"

    @staticmethod
    def all_recipes(group_id: UUID4 | str) -> str:
        return f"{Routes.base}/{group_id}"

    @staticmethod
    def recipe(groud_id: str | UUID4, recipe_slug: str | UUID4) -> str:
        return f"{Routes.base}/{groud_id}/{recipe_slug}"


@dataclass(slots=True)
class PublicRecipeTestCase:
    private_group: bool
    public_recipe: bool
    status_code: int
    error: str | None


@pytest.mark.parametrize(
    "test_case",
    (
        PublicRecipeTestCase(private_group=False, public_recipe=True, status_code=200, error=None),
        PublicRecipeTestCase(private_group=True, public_recipe=True, status_code=404, error="group not found"),
        PublicRecipeTestCase(private_group=False, public_recipe=False, status_code=404, error="recipe not found"),
    ),
    ids=("is public", "group private", "recipe private"),
)
def test_public_recipe_access(
    api_client: TestClient,
    unique_user: TestUser,
    random_recipe: Recipe,
    database: AllRepositories,
    test_case: PublicRecipeTestCase,
):
    group = database.groups.get_one(unique_user.group_id)
    group.preferences.private_group = test_case.private_group
    database.group_preferences.update(group.id, group.preferences)

    # Set Recipe `settings.public` attribute
    random_recipe.settings.public = test_case.public_recipe
    database.recipes.update(random_recipe.slug, random_recipe)

    # Try to access recipe
    response = api_client.get(Routes.recipe(random_recipe.group_id, random_recipe.slug))
    assert response.status_code == test_case.status_code

    if test_case.error:
        assert response.json()["detail"] == test_case.error
        return

    as_json = response.json()
    assert as_json["name"] == random_recipe.name
    assert as_json["slug"] == random_recipe.slug


@pytest.fixture()
def test_recipes(
    unique_user: TestUser, database: AllRepositories
) -> Generator[tuple[list[Recipe], list[str]], None, None]:
    created_ids: list[str] = []
    recipes: list[Recipe] = []
    for _ in range(10):
        data = Recipe(
            name=random_string(10),
            group_id=unique_user.group_id,
        )

        recipe = database.recipes.create(data)
        recipe.settings.public = True
        result = database.recipes.update(recipe.slug, recipe)
        created_ids.append(str(result.id))
        recipes.append(result)

    try:
        yield recipes, created_ids
    finally:
        for recipe in recipes:
            database.recipes.delete(recipe.slug)


@pytest.mark.parametrize(
    "test_case",
    (
        PublicRecipeTestCase(private_group=False, public_recipe=True, status_code=200, error=None),
        PublicRecipeTestCase(private_group=True, public_recipe=True, status_code=404, error="group not found"),
        PublicRecipeTestCase(private_group=False, public_recipe=True, status_code=200, error=None),
    ),
    ids=("is public", "group private", "public group w/ private recipe"),
)
def test_public_recipe_get_all(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    test_case: PublicRecipeTestCase,
    test_recipes: tuple[list[Recipe], list[str]],
):
    # Setup
    recipes, created_ids = test_recipes

    # Set Group `preferences.private_group` attribute
    group = database.groups.get_one(unique_user.group_id)
    group.preferences.private_group = test_case.private_group
    database.group_preferences.update(group.id, group.preferences)

    # Set Recipe `settings.public` attribute
    for recipe in recipes:
        recipe.settings.public = test_case.public_recipe
        database.recipes.update(recipe.slug, recipe)

    # Assert
    response = api_client.get(Routes.all_recipes(unique_user.group_id))
    assert response.status_code == test_case.status_code

    if test_case.error:
        assert response.json()["detail"] == test_case.error
        return

    body = response.json()

    if test_case.public_recipe:
        assert len(body["items"]) == 10
        for recipe_json in body["items"]:
            assert recipe_json["id"] in created_ids
    else:
        assert len(body["items"]) == 0
