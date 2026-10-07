from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.engine import Connection, ExecutionContext

from mealie.db.db_setup import engine
from mealie.schema.recipe.recipe_share_token import RecipeShareToken, RecipeShareTokenSave
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(scope="function")
def slug(api_client: TestClient, unique_user: TestUser) -> Generator[str]:
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


def test_share_recipe_from_different_group(api_client: TestClient, unique_user: TestUser, g2_user: TestUser, slug: str):
    database = unique_user.repos
    recipe = database.recipes.get_one(slug)
    assert recipe

    response = api_client.post(api_routes.shared_recipes, json={"recipeId": str(recipe.id)}, headers=g2_user.token)
    assert response.status_code == 404


def test_share_recipe_from_different_household(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser, slug: str
):
    database = unique_user.repos
    recipe = database.recipes.get_one(slug)
    assert recipe

    response = api_client.post(api_routes.shared_recipes, json={"recipeId": str(recipe.id)}, headers=h2_user.token)
    assert response.status_code == 201


def test_get_recipe_from_token(api_client: TestClient, unique_user: TestUser, slug: str):
    database = unique_user.repos
    recipe = database.recipes.get_one(slug)
    assert recipe

    token = database.recipe_share_tokens.create(
        RecipeShareTokenSave(recipe_id=recipe.id, group_id=unique_user.group_id)
    )

    response = api_client.get(api_routes.recipes_shared_token_id(token.id))
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == str(recipe.id)


def test_get_recipe_from_expired_token_deletes_token_and_returns_404(
    api_client: TestClient, unique_user: TestUser, slug: str
):
    database = unique_user.repos
    recipe = database.recipes.get_one(slug)
    assert recipe

    token = database.recipe_share_tokens.create(
        RecipeShareTokenSave(
            recipe_id=recipe.id, group_id=unique_user.group_id, expiresAt=datetime.now(UTC) - timedelta(minutes=1)
        )
    )
    fetch_token = database.recipe_share_tokens.get_one(token.id)
    assert fetch_token

    response = api_client.get(api_routes.recipes_shared_token_id(token.id), headers=unique_user.token)
    assert response.status_code == 404

    fetch_token = database.recipe_share_tokens.get_one(token.id)
    assert fetch_token is None


@pytest.mark.parametrize("operation", ["public", "token", "list", "create"])
def test_shared_recipe_collections_do_not_multiply_query_rows(
    api_client: TestClient, unique_user: TestUser, slug: str, operation: str
) -> None:
    response = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert response.status_code == 200
    payload = response.json()
    payload.update(
        recipeIngredient=[{"note": f"Ingredient {index}"} for index in range(6)],
        recipeInstructions=[{"text": f"Step {index}"} for index in range(4)],
        notes=[{"title": f"Note {index}", "text": f"Note text {index}"} for index in range(3)],
        recipeCategory=[{"name": random_string(12)} for _ in range(2)],
        tags=[{"name": random_string(12)} for _ in range(3)],
        tools=[{"name": random_string(12)} for _ in range(2)],
    )
    response = api_client.put(api_routes.recipes_slug(slug), json=payload, headers=unique_user.token)
    assert response.status_code == 200
    expected = response.json()
    token = unique_user.repos.recipe_share_tokens.create(
        RecipeShareTokenSave(recipe_id=expected["id"], group_id=unique_user.group_id)
    )
    row_counts: list[int] = []

    def count_query_rows(
        connection: Connection,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: ExecutionContext,
        executemany: bool,
    ) -> None:
        if context.execution_options.get("count_shared_recipe_rows") or not statement.lstrip().startswith("SELECT"):
            return
        # Count the actual SQL result before ORM deduplication, without consuming its cursor.
        # This catches a Cartesian explosion even when the returned recipe looks correct.
        count = connection.exec_driver_sql(
            f"SELECT COUNT(*) FROM ({statement}) AS shared_recipe_row_count",
            parameters,
            execution_options={"count_shared_recipe_rows": True},
        ).scalar_one()
        row_counts.append(count)

    event.listen(engine, "before_cursor_execute", count_query_rows)
    try:
        match operation:
            case "public":
                response = api_client.get(api_routes.recipes_shared_token_id(token.id))
            case "token":
                response = api_client.get(api_routes.shared_recipes_item_id(token.id), headers=unique_user.token)
            case "list":
                response = api_client.get(
                    api_routes.shared_recipes, params={"recipe_id": expected["id"]}, headers=unique_user.token
                )
            case "create":
                response = api_client.post(
                    api_routes.shared_recipes, json={"recipeId": expected["id"]}, headers=unique_user.token
                )
    finally:
        event.remove(engine, "before_cursor_execute", count_query_rows)

    assert response.status_code == (201 if operation == "create" else 200)
    assert row_counts
    # Independent collections have at most six entries. Joining them together produces 864 rows.
    assert max(row_counts) <= 6, row_counts
    data = response.json()
    if operation == "list":
        assert len(data) == 1
        assert data[0]["recipeId"] == expected["id"]
        return
    shared_recipe = data if operation == "public" else data["recipe"]
    for field in ("recipeIngredient", "recipeInstructions", "notes", "recipeCategory", "tags", "tools"):
        assert shared_recipe[field] == expected[field]
