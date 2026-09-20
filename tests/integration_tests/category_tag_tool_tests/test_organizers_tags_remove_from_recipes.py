"""
Integration tests for POST /organizers/tags/{item_id}/remove-from-recipes
"""

import uuid

from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _create_tag(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(api_routes.organizers_tags, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _create_recipe(api_client: TestClient, user: TestUser) -> str:
    """Creates a recipe and returns its slug."""
    response = api_client.post(api_routes.recipes, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _set_recipe_tags(api_client: TestClient, user: TestUser, slug: str, tags: list[dict]) -> None:
    response = api_client.get(api_routes.recipes_slug(slug), headers=user.token)
    assert response.status_code == 200
    body = response.json()
    body["tags"] = [{"id": t["id"], "groupId": user.group_id, "name": t["name"], "slug": t["slug"]} for t in tags]
    response = api_client.put(api_routes.recipes_slug(slug), json=body, headers=user.token)
    assert response.status_code == 200


def test_remove_from_recipes_removes_tag_from_only_the_given_recipes(api_client: TestClient, unique_user: TestUser):
    tag = _create_tag(api_client, unique_user)
    other_tag = _create_tag(api_client, unique_user)

    slug1 = _create_recipe(api_client, unique_user)
    slug2 = _create_recipe(api_client, unique_user)
    slug3 = _create_recipe(api_client, unique_user)
    _set_recipe_tags(api_client, unique_user, slug1, [tag])
    _set_recipe_tags(api_client, unique_user, slug2, [tag, other_tag])
    _set_recipe_tags(api_client, unique_user, slug3, [tag])

    recipe1 = api_client.get(api_routes.recipes_slug(slug1), headers=unique_user.token).json()
    recipe2 = api_client.get(api_routes.recipes_slug(slug2), headers=unique_user.token).json()

    response = api_client.post(
        api_routes.organizers_tags_item_id_remove_from_recipes(tag["id"]),
        json={"recipeIds": [recipe1["id"], recipe2["id"]]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == tag["id"]
    # only slug3 still has the tag
    assert result["recipeCount"] == 1

    recipe1_after = api_client.get(api_routes.recipes_slug(slug1), headers=unique_user.token).json()
    recipe2_after = api_client.get(api_routes.recipes_slug(slug2), headers=unique_user.token).json()
    recipe3_after = api_client.get(api_routes.recipes_slug(slug3), headers=unique_user.token).json()

    assert tag["id"] not in [t["id"] for t in recipe1_after["tags"]]

    recipe2_tag_ids = [t["id"] for t in recipe2_after["tags"]]
    assert tag["id"] not in recipe2_tag_ids
    assert other_tag["id"] in recipe2_tag_ids  # unrelated tag on the same recipe is untouched

    assert tag["id"] in [t["id"] for t in recipe3_after["tags"]]  # untouched recipe keeps the tag

    # the tag itself still exists (only its recipe associations were removed)
    assert api_client.get(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token).status_code == 200

    api_client.delete(api_routes.recipes_slug(slug1), headers=unique_user.token)
    api_client.delete(api_routes.recipes_slug(slug2), headers=unique_user.token)
    api_client.delete(api_routes.recipes_slug(slug3), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(other_tag["id"]), headers=unique_user.token)


def test_remove_from_recipes_unknown_tag_id_returns_404(api_client: TestClient, unique_user: TestUser):
    slug = _create_recipe(api_client, unique_user)
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()

    response = api_client.post(
        api_routes.organizers_tags_item_id_remove_from_recipes(str(uuid.uuid4())),
        json={"recipeIds": [recipe["id"]]},
        headers=unique_user.token,
    )
    assert response.status_code == 404

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)


def test_remove_from_recipes_empty_recipe_list_is_a_noop(api_client: TestClient, unique_user: TestUser):
    tag = _create_tag(api_client, unique_user)
    slug = _create_recipe(api_client, unique_user)
    _set_recipe_tags(api_client, unique_user, slug, [tag])

    response = api_client.post(
        api_routes.organizers_tags_item_id_remove_from_recipes(tag["id"]),
        json={"recipeIds": []},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    assert response.json()["recipeCount"] == 1

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token)
