from collections.abc import Generator
from pathlib import Path

import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from mealie.core.dependencies.dependencies import validate_file_token
from mealie.schema.recipe.recipe_bulk_actions import ExportTypes
from mealie.schema.recipe.recipe_category import CategorySave, TagSave
from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(scope="function")
def ten_slugs(api_client: TestClient, unique_user: TestUser) -> Generator[list[str], None, None]:
    database = unique_user.repos
    slugs: list[str] = []

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


def test_bulk_tag_recipes(api_client: TestClient, unique_user: TestUser, ten_slugs: list[str]):
    database = unique_user.repos

    # Setup Tags
    tags = []
    for _ in range(3):
        tag_name = random_string()
        tag = database.tags.create(TagSave(group_id=unique_user.group_id, name=tag_name))
        tags.append(tag.model_dump())

    payload = {"recipes": ten_slugs, "tags": tags}

    response = api_client.post(
        api_routes.recipes_bulk_actions_tag, json=utils.jsonify(payload), headers=unique_user.token
    )
    assert response.status_code == 200

    # Validate Recipes are Tagged
    for slug in ten_slugs:
        recipe = database.recipes.get_one(slug)

        for tag in recipe.tags:  # type: ignore
            assert tag.slug in [x["slug"] for x in tags]


def test_bulk_categorize_recipes(
    api_client: TestClient,
    unique_user: TestUser,
    ten_slugs: list[str],
):
    database = unique_user.repos

    # Setup Tags
    categories = []
    for _ in range(3):
        cat_name = random_string()
        cat = database.categories.create(CategorySave(group_id=unique_user.group_id, name=cat_name))
        categories.append(cat.model_dump())

    payload = {"recipes": ten_slugs, "categories": categories}

    response = api_client.post(
        api_routes.recipes_bulk_actions_categorize, json=utils.jsonify(payload), headers=unique_user.token
    )
    assert response.status_code == 200

    # Validate Recipes are Categorized
    for slug in ten_slugs:
        recipe = database.recipes.get_one(slug)

        for cat in recipe.recipe_category:  # type: ignore
            assert cat.slug in [x["slug"] for x in categories]


def test_bulk_delete_recipes(
    api_client: TestClient,
    unique_user: TestUser,
    ten_slugs: list[str],
):
    database = unique_user.repos
    payload = {"recipes": ten_slugs}

    response = api_client.post(api_routes.recipes_bulk_actions_delete, json=payload, headers=unique_user.token)
    assert response.status_code == 200

    # Validate Recipes are Tagged
    for slug in ten_slugs:
        recipe = database.recipes.get_one(slug)
        assert recipe is None


def test_bulk_export_recipes(api_client: TestClient, unique_user: TestUser, ten_slugs: list[str]):
    payload = {
        "recipes": ten_slugs,
        "export_type": ExportTypes.JSON.value,
    }

    response = api_client.post(api_routes.recipes_bulk_actions_export, json=payload, headers=unique_user.token)
    assert response.status_code == 202

    # Get All Exports Available
    response = api_client.get(api_routes.recipes_bulk_actions_export, headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 1

    export_path = response_data[0]["path"]

    # Get Export Token
    response = api_client.get(
        f"{api_routes.recipes_bulk_actions_export_download}?path={export_path}", headers=unique_user.token
    )
    assert response.status_code == 200

    response_data = response.json()

    assert validate_file_token(response_data["fileToken"]) == Path(export_path)

    # Use Export Token to download export
    response = api_client.get(f"/api/utils/download?token={response_data['fileToken']}")

    assert response.status_code == 200

    # Smoke Test to check that a file was downloaded
    assert response.headers["Content-Type"] == "application/octet-stream"
    assert len(response.content) > 0

    # Purge Export
    response = api_client.delete(api_routes.recipes_bulk_actions_export_purge, headers=unique_user.token)
    assert response.status_code == 200

    # Validate Export was purged
    response = api_client.get(api_routes.recipes_bulk_actions_export, headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 0
