import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.schema.recipe.recipe import Recipe
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/comments"
    recipes = "/api/recipes"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"

    def recipe(recipe_id: int) -> str:
        return f"{Routes.recipes}/{recipe_id}"

    def recipe_comments(recipe_slug: str) -> str:
        return f"{Routes.recipe(recipe_slug)}/comments"


@pytest.fixture(scope="function")
def unique_recipe(api_client: TestClient, unique_user: TestUser):
    payload = {"name": random_string(length=20)}
    response = api_client.post(Routes.recipes, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    response_data = response.json()
    recipe_response = api_client.get(Routes.recipe(response_data), headers=unique_user.token)

    return Recipe(**recipe_response.json())


def random_comment(recipe_id: UUID4) -> dict:
    if recipe_id is None:
        raise ValueError("recipe_id is required")
    return {
        "recipeId": str(recipe_id),
        "text": random_string(length=50),
    }


def test_create_comment(api_client: TestClient, unique_recipe: Recipe, unique_user: TestUser):
    # Create Comment
    create_data = random_comment(unique_recipe.id)
    response = api_client.post(Routes.base, json=create_data, headers=unique_user.token)
    assert response.status_code == 201

    response_data = response.json()

    assert response_data["recipeId"] == str(unique_recipe.id)
    assert response_data["text"] == create_data["text"]
    assert response_data["userId"] == unique_user.user_id

    # Check for Proper Association
    response = api_client.get(Routes.recipe_comments(unique_recipe.slug), headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data) == 1
    assert response_data[0]["recipeId"] == str(unique_recipe.id)
    assert response_data[0]["text"] == create_data["text"]
    assert response_data[0]["userId"] == unique_user.user_id


def test_update_comment(api_client: TestClient, unique_recipe: Recipe, unique_user: TestUser):
    # Create Comment
    create_data = random_comment(unique_recipe.id)
    response = api_client.post(Routes.base, json=create_data, headers=unique_user.token)
    assert response.status_code == 201

    comment_id = response.json()["id"]

    # Update Comment
    update_data = random_comment(unique_recipe.id)
    update_data["id"] = comment_id

    response = api_client.put(Routes.item(comment_id), json=update_data, headers=unique_user.token)

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["recipeId"] == str(unique_recipe.id)
    assert response_data["text"] == update_data["text"]
    assert response_data["userId"] == unique_user.user_id


def test_delete_comment(api_client: TestClient, unique_recipe: Recipe, unique_user: TestUser):
    # Create Comment
    create_data = random_comment(unique_recipe.id)
    response = api_client.post(Routes.base, json=create_data, headers=unique_user.token)
    assert response.status_code == 201

    # Delete Comment
    comment_id = response.json()["id"]
    response = api_client.delete(Routes.item(comment_id), headers=unique_user.token)
    assert response.status_code == 200

    # Validate Deletion
    response = api_client.get(Routes.item(comment_id), headers=unique_user.token)

    assert response.status_code == 404


def test_admin_can_delete(api_client: TestClient, unique_recipe: Recipe, unique_user: TestUser, admin_user: TestUser):
    # Create Comment
    create_data = random_comment(unique_recipe.id)
    response = api_client.post(Routes.base, json=create_data, headers=unique_user.token)
    assert response.status_code == 201

    # Delete Comment
    comment_id = response.json()["id"]
    response = api_client.delete(Routes.item(comment_id), headers=admin_user.token)
    assert response.status_code == 200

    # Validate Deletion
    response = api_client.get(Routes.item(comment_id), headers=admin_user.token)

    assert response.status_code == 404
