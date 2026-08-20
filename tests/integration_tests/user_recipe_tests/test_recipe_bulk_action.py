from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from mealie.core.dependencies.dependencies import validate_file_token
from mealie.schema.recipe.recipe_bulk_actions import ExportTypes
from mealie.schema.recipe.recipe_category import CategorySave, TagSave
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.event_types import EventTypes
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


def _create_recipe(api_client: TestClient, user: TestUser) -> str:
    response = api_client.post(api_routes.recipes, json={"name": random_string(length=20)}, headers=user.token)
    assert response.status_code == 201
    recipe = user.repos.recipes.get_one(response.json())
    assert recipe and recipe.id
    return str(recipe.id)


def test_bulk_organize_add_remove_is_atomic_and_idempotent(api_client: TestClient, unique_user: TestUser):
    recipe_ids = [_create_recipe(api_client, unique_user) for _ in range(2)]
    tag = unique_user.repos.tags.create(TagSave(group_id=unique_user.group_id, name=random_string()))
    category = unique_user.repos.categories.create(CategorySave(group_id=unique_user.group_id, name=random_string()))
    organizer_payload = {
        "recipes": recipe_ids,
        "operation": "add",
        "tags": [tag.model_dump(), tag.model_dump()],
        "categories": [category.model_dump(), category.model_dump()],
    }

    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(organizer_payload),
        headers=unique_user.token,
    )
    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == set(recipe_ids)

    for recipe_id in recipe_ids:
        recipe = unique_user.repos.recipes.get_one(recipe_id, key="id")
        assert recipe
        assert [item.id for item in recipe.tags] == [tag.id]  # type: ignore
        assert [item.id for item in recipe.recipe_category] == [category.id]  # type: ignore

    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(organizer_payload),
        headers=unique_user.token,
    )
    assert response.status_code == 200
    assert response.json() == []

    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify({**organizer_payload, "operation": "remove"}),
        headers=unique_user.token,
    )
    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == set(recipe_ids)
    for recipe_id in recipe_ids:
        recipe = unique_user.repos.recipes.get_one(recipe_id, key="id")
        assert recipe and not recipe.tags and not recipe.recipe_category


def test_bulk_organize_empty_fields_leave_other_organizers_unchanged(api_client: TestClient, unique_user: TestUser):
    recipe_id = _create_recipe(api_client, unique_user)
    tag = unique_user.repos.tags.create(TagSave(group_id=unique_user.group_id, name=random_string()))
    category = unique_user.repos.categories.create(CategorySave(group_id=unique_user.group_id, name=random_string()))

    add_category_response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(
            {
                "recipes": [recipe_id],
                "operation": "add",
                "tags": [],
                "categories": [category.model_dump()],
            }
        ),
        headers=unique_user.token,
    )
    assert add_category_response.status_code == 200

    add_tag_response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(
            {
                "recipes": [recipe_id],
                "operation": "add",
                "tags": [tag.model_dump()],
                "categories": [],
            }
        ),
        headers=unique_user.token,
    )
    assert add_tag_response.status_code == 200

    recipe = unique_user.repos.recipes.get_one(recipe_id, key="id")
    assert recipe
    assert [item.id for item in recipe.tags] == [tag.id]  # type: ignore
    assert [item.id for item in recipe.recipe_category] == [category.id]  # type: ignore

    remove_tag_response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(
            {
                "recipes": [recipe_id],
                "operation": "remove",
                "tags": [tag.model_dump()],
                "categories": [],
            }
        ),
        headers=unique_user.token,
    )
    assert remove_tag_response.status_code == 200

    recipe = unique_user.repos.recipes.get_one(recipe_id, key="id")
    assert recipe and not recipe.tags
    assert [item.id for item in recipe.recipe_category] == [category.id]  # type: ignore


def test_bulk_organize_empty_selection_is_a_noop(api_client: TestClient, unique_user: TestUser):
    recipe_id = _create_recipe(api_client, unique_user)
    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json={"recipes": [recipe_id], "operation": "add", "tags": [], "categories": []},
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_bulk_organize_invalid_organizer_does_not_change_targets(api_client: TestClient, unique_user: TestUser):
    recipe_id = _create_recipe(api_client, unique_user)
    missing_tag_id = uuid4()
    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json={
            "recipes": [recipe_id],
            "operation": "add",
            "tags": [{"id": str(missing_tag_id), "name": "Missing", "slug": "missing"}],
            "categories": [],
        },
        headers=unique_user.token,
    )

    assert response.status_code == 404
    recipe = unique_user.repos.recipes.get_one(recipe_id, key="id")
    assert recipe and not recipe.tags


def test_bulk_organize_cross_group_organizer_does_not_change_targets(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser
):
    recipe_id = _create_recipe(api_client, unique_user)
    foreign_tag = g2_user.repos.tags.create(TagSave(group_id=g2_user.group_id, name=random_string()))

    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(
            {
                "recipes": [recipe_id],
                "operation": "add",
                "tags": [foreign_tag.model_dump()],
                "categories": [],
            }
        ),
        headers=unique_user.token,
    )

    assert response.status_code == 404
    recipe = unique_user.repos.recipes.get_one(recipe_id, key="id")
    assert recipe and not recipe.tags


def test_bulk_organize_locked_recipe_rolls_back_prior_targets(
    api_client: TestClient, user_tuple: list[TestUser], monkeypatch: pytest.MonkeyPatch
):
    owner, editor = user_tuple
    recipe_ids = [_create_recipe(api_client, owner) for _ in range(2)]
    locked_recipe = owner.repos.recipes.get_one(recipe_ids[1], key="id")
    assert locked_recipe and locked_recipe.settings
    locked_recipe.settings = RecipeSettings(locked=True)
    owner.repos.recipes.update(locked_recipe.slug, locked_recipe)
    tag = owner.repos.tags.create(TagSave(group_id=owner.group_id, name=random_string()))
    dispatched_events = []

    def capture_dispatch(_service: EventBusService, **kwargs):
        dispatched_events.append(kwargs)

    monkeypatch.setattr(EventBusService, "dispatch", capture_dispatch)

    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(
            {
                "recipes": recipe_ids,
                "operation": "add",
                "tags": [tag.model_dump()],
                "categories": [],
            }
        ),
        headers=editor.token,
    )

    assert response.status_code == 403
    for recipe_id in recipe_ids:
        recipe = owner.repos.recipes.get_one(recipe_id, key="id")
        assert recipe and not recipe.tags
    assert dispatched_events == []


def test_bulk_organize_missing_target_does_not_change_valid_recipe(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser
):
    recipe_id = _create_recipe(api_client, unique_user)
    foreign_recipe_id = _create_recipe(api_client, g2_user)
    tag = unique_user.repos.tags.create(TagSave(group_id=unique_user.group_id, name=random_string()))

    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(
            {
                "recipes": [recipe_id, foreign_recipe_id],
                "operation": "add",
                "tags": [tag.model_dump()],
                "categories": [],
            }
        ),
        headers=unique_user.token,
    )

    assert response.status_code == 404
    recipe = unique_user.repos.recipes.get_one(recipe_id, key="id")
    assert recipe and not recipe.tags


def test_bulk_organize_cross_household_policy_rolls_back_prior_targets(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser
):
    other_household = h2_user.repos.households.get_one(h2_user.household_id)
    assert other_household and other_household.preferences
    other_household.preferences.lock_recipe_edits_from_other_households = True
    h2_user.repos.household_preferences.update(other_household.id, other_household.preferences)

    owned_recipe_id = _create_recipe(api_client, unique_user)
    foreign_recipe_id = _create_recipe(api_client, h2_user)
    tag = unique_user.repos.tags.create(TagSave(group_id=unique_user.group_id, name=random_string()))

    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(
            {
                "recipes": [owned_recipe_id, foreign_recipe_id],
                "operation": "add",
                "tags": [tag.model_dump()],
                "categories": [],
            }
        ),
        headers=unique_user.token,
    )

    assert response.status_code == 403
    owned_recipe = unique_user.repos.recipes.get_one(owned_recipe_id, key="id")
    foreign_recipe = h2_user.repos.recipes.get_one(foreign_recipe_id, key="id")
    assert owned_recipe and not owned_recipe.tags
    assert foreign_recipe and not foreign_recipe.tags


def test_bulk_organize_events_only_publish_for_changed_batches(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    recipe_ids = [_create_recipe(api_client, unique_user) for _ in range(2)]
    tag = unique_user.repos.tags.create(TagSave(group_id=unique_user.group_id, name=random_string()))
    dispatched_events = []

    def capture_dispatch(_service: EventBusService, **kwargs):
        dispatched_events.append(kwargs)

    monkeypatch.setattr(EventBusService, "dispatch", capture_dispatch)
    payload = {
        "recipes": recipe_ids,
        "operation": "add",
        "tags": [tag.model_dump()],
        "categories": [],
    }

    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(payload),
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert len(dispatched_events) == 1
    assert dispatched_events[0]["event_type"] == EventTypes.recipe_updated
    assert dispatched_events[0]["document_data"].recipe_slugs == [
        unique_user.repos.recipes.get_one(recipe_id, key="id").slug
        for recipe_id in recipe_ids  # type: ignore[union-attr]
    ]

    dispatched_events.clear()
    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(payload),
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert response.json() == []
    assert dispatched_events == []

    dispatched_events.clear()
    response = api_client.post(
        api_routes.recipes_bulk_actions_organize,
        json=utils.jsonify(
            {
                **payload,
                "tags": [{"id": str(uuid4()), "name": "Missing", "slug": "missing"}],
            }
        ),
        headers=unique_user.token,
    )

    assert response.status_code == 404
    assert dispatched_events == []
