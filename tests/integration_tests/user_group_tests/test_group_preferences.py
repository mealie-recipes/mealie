from fastapi.testclient import TestClient

from mealie.schema.group.group_preferences import UpdateGroupPreferences
from mealie.repos.repository_factory import AllRepositories
from tests.utils import api_routes, jsonify
from tests.utils.assertion_helpers import assert_ignore_keys
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_get_preferences(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(api_routes.groups_preferences, headers=unique_user.token)
    assert response.status_code == 200

    preferences = response.json()

    assert preferences["recipePublic"] in {True, False}
    assert preferences["recipeShowNutrition"] in {True, False}


def test_preferences_in_group(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(api_routes.groups_self, headers=unique_user.token)

    assert response.status_code == 200

    group = response.json()

    assert group["preferences"] is not None

    # Spot Check
    assert group["preferences"]["recipePublic"] in {True, False}
    assert group["preferences"]["recipeShowNutrition"] in {True, False}


def test_update_preferences(database: AllRepositories, api_client: TestClient, unique_user: TestUser) -> None:
    # Postgres enforces foreign key on the test (good!),
    # whereas SQLite does not, so we need to create a tag first.
    tag = database.tags.by_group(unique_user.group_id).create(
        {"name": random_string(), "group_id": unique_user.group_id}
    )

    new_data = UpdateGroupPreferences(
        recipe_public=False,
        recipe_show_nutrition=True,
        recipe_show_assets=True,
        recipe_landscape_view=True,
        recipe_disable_comments=True,
        recipe_disable_amount=False,
        recipe_creation_tag=tag.id,
    )

    response = api_client.put(api_routes.groups_preferences, json=jsonify(new_data.dict()), headers=unique_user.token)

    assert response.status_code == 200

    preferences = response.json()

    assert preferences is not None
    assert preferences["recipeCreationTag"] == jsonify(tag.id)

    # We ignore recipeCreationTag here because the json (`preferences`) has it as a string,
    # because of the jsonify, whereas new_data has it as a UUID. We verify it above instead.
    assert_ignore_keys(new_data.dict(by_alias=True), preferences, ["id", "groupId", "recipeCreationTag"])
