from typing import Generator

import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(scope="function")
def ten_slugs(
    api_client: TestClient, unique_user: TestUser, database: AllRepositories
) -> Generator[list[str], None, None]:
    slugs = []

    for _ in range(10):
        payload = {"name": random_string(length=20)}
        response = api_client.post(api_routes.recipes, json=payload, headers=unique_user.token)
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
    response = api_client.get(api_routes.users_id_favorites(unique_user.user_id), headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["favoriteRecipes"] == []

    # Add a few recipes to the user's favorites
    for slug in ten_slugs:
        response = api_client.post(
            api_routes.users_id_favorites_slug(unique_user.user_id, slug), headers=unique_user.token
        )
        assert response.status_code == 200

    # Check that the user has the recipes in their favorites
    response = api_client.get(api_routes.users_id_favorites(unique_user.user_id), headers=unique_user.token)
    assert response.status_code == 200
    assert len(response.json()["favoriteRecipes"]) == 10

    # Remove a few recipes from the user's favorites
    for slug in ten_slugs[:5]:
        response = api_client.delete(
            api_routes.users_id_favorites_slug(unique_user.user_id, slug), headers=unique_user.token
        )
        assert response.status_code == 200

    # Check that the user has the recipes in their favorites
    response = api_client.get(api_routes.users_id_favorites(unique_user.user_id), headers=unique_user.token)
    assert response.status_code == 200
    assert len(response.json()["favoriteRecipes"]) == 5
