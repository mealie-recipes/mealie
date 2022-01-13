from pathlib import Path

import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from mealie.core.dependencies.dependencies import validate_file_token
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe_bulk_actions import ExportTypes
from mealie.schema.recipe.recipe_category import TagIn
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    create_recipes = "/api/recipes"

    bulk_tag = "api/recipes/bulk-actions/tag"
    bulk_categorize = "api/recipes/bulk-actions/categorize"
    bulk_delete = "api/recipes/bulk-actions/delete"

    bulk_export = "api/recipes/bulk-actions/export"
    bulk_export_download = bulk_export + "/download"
    bulk_export_purge = bulk_export + "/purge"


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


def test_bulk_tag_recipes(
    api_client: TestClient, unique_user: TestUser, database: AllRepositories, ten_slugs: list[str]
):
    # Setup Tags
    tags = []
    for _ in range(3):
        tag_name = random_string()
        tag = database.tags.create(TagIn(name=tag_name))
        tags.append(tag.dict())

    payload = {"recipes": ten_slugs, "tags": tags}

    response = api_client.post(Routes.bulk_tag, json=payload, headers=unique_user.token)
    assert response.status_code == 200

    # Validate Recipes are Tagged
    for slug in ten_slugs:
        recipe = database.recipes.get_one(slug)

        for tag in recipe.tags:
            assert tag.slug in [x["slug"] for x in tags]


def test_bulk_categorize_recipes(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    ten_slugs: list[str],
):
    # Setup Tags
    categories = []
    for _ in range(3):
        cat_name = random_string()
        cat = database.tags.create(TagIn(name=cat_name))
        categories.append(cat.dict())

    payload = {"recipes": ten_slugs, "categories": categories}

    response = api_client.post(Routes.bulk_categorize, json=payload, headers=unique_user.token)
    assert response.status_code == 200

    # Validate Recipes are Categorized
    for slug in ten_slugs:
        recipe = database.recipes.get_one(slug)

        for cat in recipe.recipe_category:
            assert cat.slug in [x["slug"] for x in categories]


def test_bulk_delete_recipes(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    ten_slugs: list[str],
):

    payload = {"recipes": ten_slugs}

    response = api_client.post(Routes.bulk_delete, json=payload, headers=unique_user.token)
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

    response = api_client.post(Routes.bulk_export, json=payload, headers=unique_user.token)
    assert response.status_code == 202

    # Get All Exports Available
    response = api_client.get(Routes.bulk_export, headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 1

    export_path = response_data[0]["path"]

    # Get Export Token
    response = api_client.get(f"{Routes.bulk_export_download}?path={export_path}", headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()

    assert validate_file_token(response_data["fileToken"]) == Path(export_path)

    # Use Export Token to donwload export
    response = api_client.get("/api/utils/download?token=" + response_data["fileToken"])

    assert response.status_code == 200

    # Smoke Test to check that a file was downloaded
    assert response.headers["Content-Type"] == "application/octet-stream"
    assert len(response.content) > 0

    # Purge Export
    response = api_client.delete(Routes.bulk_export_purge, headers=unique_user.token)
    assert response.status_code == 200

    # Validate Export was purged
    response = api_client.get(Routes.bulk_export, headers=unique_user.token)
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 0
