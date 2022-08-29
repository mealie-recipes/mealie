from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/explore/recipes"

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
def test_public_recipe_success(
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
