from collections.abc import Generator

import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_share_token import RecipeShareToken, RecipeShareTokenSave
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(scope="function")
def slug(api_client: TestClient, unique_user: TestUser) -> Generator[str, None, None]:
    database = unique_user.repos
    payload = {"name": random_string(length=20)}
    response = api_client.post(api_routes.recipes, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    response_data = response.json()

    yield response_data

    try:
        database.recipes.delete(response_data)
    except sqlalchemy.exc.NoResultFound:
        pass


def test_recipe_share_tokens_get_all(api_client: TestClient, unique_user: TestUser, slug: str):
    database = unique_user.repos

    # Create 5 Tokens
    recipe = database.recipes.get_one(slug)
    assert recipe

    tokens = []
    for _ in range(5):
        token = database.recipe_share_tokens.create(
            RecipeShareTokenSave(recipe_id=recipe.id, group_id=unique_user.group_id)
        )
        tokens.append(token)

    # Get All Tokens
    response = api_client.get(api_routes.shared_recipes, headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 5


def test_recipe_share_tokens_get_all_with_id(api_client: TestClient, unique_user: TestUser, slug: str):
    database = unique_user.repos

    # Create 5 Tokens
    recipe = database.recipes.get_one(slug)
    assert recipe

    tokens = []
    for _ in range(3):
        token = database.recipe_share_tokens.create(
            RecipeShareTokenSave(recipe_id=recipe.id, group_id=unique_user.group_id)
        )
        tokens.append(token)

    response = api_client.get(api_routes.shared_recipes + "?recipe_id=" + str(recipe.id), headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data) == 3


def test_recipe_share_tokens_create_and_get_one(api_client: TestClient, unique_user: TestUser, slug: str):
    database = unique_user.repos
    recipe = database.recipes.get_one(slug)
    assert recipe

    payload = {
        "recipeId": str(recipe.id),
    }

    response = api_client.post(api_routes.shared_recipes, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.get(api_routes.shared_recipes_item_id(response.json()["id"]), headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["recipe"]["id"] == str(recipe.id)


def test_recipe_share_tokens_delete_one(api_client: TestClient, unique_user: TestUser, slug: str):
    database = unique_user.repos

    # Create Token
    token: RecipeShareToken | None = None
    recipe = database.recipes.get_one(slug)
    assert recipe

    token = database.recipe_share_tokens.create(
        RecipeShareTokenSave(recipe_id=recipe.id, group_id=unique_user.group_id)
    )

    # Delete Token
    response = api_client.delete(api_routes.shared_recipes_item_id(token.id), headers=unique_user.token)
    assert response.status_code == 200

    # Get Token
    token = database.recipe_share_tokens.get_one(token.id)

    assert token is None
