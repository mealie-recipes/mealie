import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe_share_token import RecipeShareTokenSave
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/shared/recipes"
    create_recipes = "/api/recipes"

    @staticmethod
    def item(item_id: str):
        return f"{Routes.base}/{item_id}"


@pytest.fixture(scope="function")
def slug(api_client: TestClient, unique_user: TestUser, database: AllRepositories) -> str:

    payload = {"name": random_string(length=20)}
    response = api_client.post(Routes.create_recipes, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    response_data = response.json()

    yield response_data

    try:
        database.recipes.delete(response_data)
    except sqlalchemy.exc.NoResultFound:
        pass


def test_recipe_share_tokens_get_all(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    slug: str,
):
    # Create 5 Tokens
    recipe = database.recipes.get_one(slug)
    tokens = []
    for _ in range(5):
        token = database.recipe_share_tokens.create(
            RecipeShareTokenSave(recipe_id=recipe.id, group_id=unique_user.group_id)
        )
        tokens.append(token)

    # Get All Tokens
    response = api_client.get(Routes.base, headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 5


def test_recipe_share_tokens_get_all_with_id(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    slug: str,
):
    # Create 5 Tokens
    recipe = database.recipes.get_one(slug)
    tokens = []
    for _ in range(3):
        token = database.recipe_share_tokens.create(
            RecipeShareTokenSave(recipe_id=recipe.id, group_id=unique_user.group_id)
        )
        tokens.append(token)

    response = api_client.get(Routes.base + "?recipe_id=" + str(recipe.id), headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data) == 3


def test_recipe_share_tokens_create_and_get_one(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    slug: str,
):
    recipe = database.recipes.get_one(slug)

    payload = {
        "recipe_id": recipe.id,
    }

    response = api_client.post(Routes.base, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.get(Routes.item(response.json()["id"]), json=payload, headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["recipe"]["id"] == recipe.id


def test_recipe_share_tokens_delete_one(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    slug: str,
):
    # Create Token
    recipe = database.recipes.get_one(slug)

    token = database.recipe_share_tokens.create(
        RecipeShareTokenSave(recipe_id=recipe.id, group_id=unique_user.group_id)
    )

    # Delete Token
    response = api_client.delete(Routes.item(token.id), headers=unique_user.token)
    assert response.status_code == 200

    # Get Token
    token = database.recipe_share_tokens.get_one(token.id)

    assert token is None
