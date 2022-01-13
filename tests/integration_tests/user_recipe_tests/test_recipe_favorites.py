import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    create_recipes = "/api/recipes"

    def base(item_id: int) -> str:
        return f"api/users/{item_id}/favorites"

    def toggle(item_id: int, slug: str) -> str:
        return f"{Routes.base(item_id)}/{slug}"


@pytest.fixture(scope="function")
def ten_slugs(api_client: TestClient, unique_user: TestUser, database: AllRepositories) -> list[str]:

    slugs = []

    for _ in range(10):
        payload = {"name": random_string(length=20)}
        response = api_client.post(Routes.create_recipes, json=payload, headers=unique_user.token)
        assert response.status_code == 201

        response_data = response.json()
        slugs.append(response_data)

    yield slugs

    for slug in slugs:
        try:
            database.recipes.delete(slug)
        except sqlalchemy.exc.NoResultFound:
            pass


def test_recipe_favorites(api_client: TestClient, unique_user: TestUser, ten_slugs: list[str]):
    # Check that the user has no favorites
    response = api_client.get(Routes.base(unique_user.user_id), headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["favoriteRecipes"] == []

    # Add a few recipes to the user's favorites
    for slug in ten_slugs:
        response = api_client.post(Routes.toggle(unique_user.user_id, slug), headers=unique_user.token)
        assert response.status_code == 200

    # Check that the user has the recipes in their favorites
    response = api_client.get(Routes.base(unique_user.user_id), headers=unique_user.token)
    assert response.status_code == 200
    assert len(response.json()["favoriteRecipes"]) == 10

    # Remove a few recipes from the user's favorites
    for slug in ten_slugs[:5]:
        response = api_client.delete(Routes.toggle(unique_user.user_id, slug), headers=unique_user.token)
        assert response.status_code == 200

    # Check that the user has the recipes in their favorites
    response = api_client.get(Routes.base(unique_user.user_id), headers=unique_user.token)
    assert response.status_code == 200
    assert len(response.json()["favoriteRecipes"]) == 5
