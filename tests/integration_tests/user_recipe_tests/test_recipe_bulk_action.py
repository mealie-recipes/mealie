from collections.abc import Generator
from pathlib import Path

import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from mealie.core.dependencies.dependencies import validate_file_token
from mealie.core.exceptions import UnexpectedNone
from mealie.schema.recipe.recipe_bulk_actions import ExportTypes
from mealie.schema.recipe.recipe_category import CategorySave, TagSave
from mealie.schema.recipe.recipe_settings import RecipeSettings
from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(scope="function")
def ten_slugs(api_client: TestClient, unique_user: TestUser) -> Generator[list[str]]:
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


def test_bulk_set_settings(
    api_client: TestClient,
    unique_user: TestUser,
    ten_slugs: list[str],
):
    database = unique_user.repos
    new_settings = RecipeSettings(
        public=True,
        show_nutrition=True,
        show_assets=True,
        landscape_view=True,
        disable_comments=False,
    )

    payload = {"recipes": ten_slugs, "settings": new_settings.model_dump(by_alias=True)}
    response = api_client.post(
        api_routes.recipes_bulk_actions_settings, json=utils.jsonify(payload), headers=unique_user.token
    )
    assert response.status_code == 200

    for slug in ten_slugs:
        recipe = database.recipes.get_one(slug)
        assert recipe is not None
        assert recipe.settings is not None
        assert recipe.settings.public is True
        assert recipe.settings.show_nutrition is True
        assert recipe.settings.show_assets is True
        assert recipe.settings.landscape_view is True
        assert recipe.settings.disable_comments is False


def test_bulk_set_settings_preserves_locked(
    api_client: TestClient,
    unique_user: TestUser,
    ten_slugs: list[str],
):
    # "locked" guards who may edit a recipe, so a bulk settings change must never be able
    # to silently unlock (or lock) a recipe - only a dedicated action should change it.
    database = unique_user.repos
    locked_slug = ten_slugs[0]

    recipe = database.recipes.get_one(locked_slug)
    assert recipe is not None
    recipe.settings.locked = True  # type: ignore
    database.recipes.update(locked_slug, recipe)

    new_settings = RecipeSettings(public=True, locked=False)
    payload = {"recipes": ten_slugs, "settings": new_settings.model_dump(by_alias=True)}
    response = api_client.post(
        api_routes.recipes_bulk_actions_settings, json=utils.jsonify(payload), headers=unique_user.token
    )
    assert response.status_code == 200

    recipe = database.recipes.get_one(locked_slug)
    assert recipe is not None
    assert recipe.settings.locked is True  # type: ignore
    assert recipe.settings.public is True  # type: ignore


def test_bulk_set_settings_does_not_leak_across_groups(
    api_client: TestClient,
    unique_user: TestUser,
    g2_user: TestUser,
    ten_slugs: list[str],
):
    # g2_user belongs to a different group; its recipe must be unreachable through
    # unique_user's bulk-settings call, even when its slug is included in the payload.
    other_database = g2_user.repos
    other_payload = {"name": random_string(length=20)}
    response = api_client.post(api_routes.recipes, json=other_payload, headers=g2_user.token)
    assert response.status_code == 201
    other_slug = response.json()

    new_settings = RecipeSettings(public=True)
    payload = {"recipes": [*ten_slugs, other_slug], "settings": new_settings.model_dump(by_alias=True)}
    # the foreign slug resolves to None under unique_user's group-scoped repos, which the
    # service surfaces as an unhandled UnexpectedNone (a 500) rather than quietly skipping it
    with pytest.raises(UnexpectedNone):
        api_client.post(
            api_routes.recipes_bulk_actions_settings, json=utils.jsonify(payload), headers=unique_user.token
        )

    other_recipe = other_database.recipes.get_one(other_slug)
    assert other_recipe is not None
    assert other_recipe.settings.public is False  # type: ignore

    other_database.recipes.delete(other_slug)


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

    export_id = response_data[0]["id"]
    export_path = response_data[0]["path"]

    # Get Export Token
    response = api_client.get(
        f"{api_routes.recipes_bulk_actions_export_export_id_download(export_id)}", headers=unique_user.token
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
