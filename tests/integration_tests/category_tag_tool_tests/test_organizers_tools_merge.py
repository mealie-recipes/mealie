"""
Integration tests for:
- recipe_count field on GET /organizers/tools
- GET /organizers/tools/empty
- POST /organizers/tools/merge
"""

import uuid

from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

TOOLS_MERGE = "/api/organizers/tools/merge"


def _create_tool(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(api_routes.organizers_tools, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _create_recipe(api_client: TestClient, user: TestUser) -> str:
    """Creates a recipe and returns its slug."""
    response = api_client.post(api_routes.recipes, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _set_recipe_tools(api_client: TestClient, user: TestUser, slug: str, tools: list[dict]) -> None:
    response = api_client.get(api_routes.recipes_slug(slug), headers=user.token)
    assert response.status_code == 200
    body = response.json()
    body["tools"] = [{"id": t["id"], "groupId": user.group_id, "name": t["name"], "slug": t["slug"]} for t in tools]
    response = api_client.put(api_routes.recipes_slug(slug), json=body, headers=user.token)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Tools — recipe_count
# ---------------------------------------------------------------------------


def test_tool_list_includes_recipe_count_for_used_tool(api_client: TestClient, unique_user: TestUser):
    tool = _create_tool(api_client, unique_user)
    slug = _create_recipe(api_client, unique_user)
    _set_recipe_tools(api_client, unique_user, slug, [tool])

    response = api_client.get(api_routes.organizers_tools, headers=unique_user.token)
    assert response.status_code == 200
    items = response.json()["items"]
    match = next((t for t in items if t["id"] == tool["id"]), None)
    assert match is not None
    assert match["recipeCount"] == 1

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tools_item_id(tool["id"]), headers=unique_user.token)


def test_tool_list_recipe_count_is_zero_for_unused_tool(api_client: TestClient, unique_user: TestUser):
    tool = _create_tool(api_client, unique_user)

    response = api_client.get(api_routes.organizers_tools, headers=unique_user.token)
    assert response.status_code == 200
    items = response.json()["items"]
    match = next((t for t in items if t["id"] == tool["id"]), None)
    assert match is not None
    assert match["recipeCount"] == 0

    api_client.delete(api_routes.organizers_tools_item_id(tool["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Tools — empty
# ---------------------------------------------------------------------------


def test_tools_empty_includes_unused_tool_and_excludes_used_tool(api_client: TestClient, unique_user: TestUser):
    unused_tool = _create_tool(api_client, unique_user)
    used_tool = _create_tool(api_client, unique_user)
    slug = _create_recipe(api_client, unique_user)
    _set_recipe_tools(api_client, unique_user, slug, [used_tool])

    response = api_client.get(api_routes.organizers_tools_empty, headers=unique_user.token)
    assert response.status_code == 200
    ids = [t["id"] for t in response.json()]
    assert unused_tool["id"] in ids
    assert used_tool["id"] not in ids

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tools_item_id(unused_tool["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tools_item_id(used_tool["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Tools — merge
# ---------------------------------------------------------------------------


def test_tool_merge_moves_exclusive_recipes_to_target(api_client: TestClient, unique_user: TestUser):
    """Recipes belonging only to from_tool are reassigned to to_tool."""
    from_tool = _create_tool(api_client, unique_user)
    to_tool = _create_tool(api_client, unique_user)

    slug1 = _create_recipe(api_client, unique_user)
    slug2 = _create_recipe(api_client, unique_user)
    _set_recipe_tools(api_client, unique_user, slug1, [from_tool])
    _set_recipe_tools(api_client, unique_user, slug2, [to_tool])

    response = api_client.post(
        TOOLS_MERGE,
        json={"fromId": from_tool["id"], "toId": to_tool["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == to_tool["id"]
    assert result["recipeCount"] == 2

    # from_tool must be deleted
    assert (
        api_client.get(api_routes.organizers_tools_item_id(from_tool["id"]), headers=unique_user.token).status_code
        == 404
    )

    # both recipes must carry to_tool
    for slug in (slug1, slug2):
        recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
        tool_ids = [t["id"] for t in recipe["tools"]]
        assert to_tool["id"] in tool_ids
        assert from_tool["id"] not in tool_ids

    api_client.delete(api_routes.recipes_slug(slug1), headers=unique_user.token)
    api_client.delete(api_routes.recipes_slug(slug2), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tools_item_id(to_tool["id"]), headers=unique_user.token)


def test_tool_merge_overlap_does_not_violate_unique_constraint(api_client: TestClient, unique_user: TestUser):
    """A recipe that already has both from_tool and to_tool must not cause a DB unique-constraint error."""
    from_tool = _create_tool(api_client, unique_user)
    to_tool = _create_tool(api_client, unique_user)

    slug = _create_recipe(api_client, unique_user)
    _set_recipe_tools(api_client, unique_user, slug, [from_tool, to_tool])

    response = api_client.post(
        TOOLS_MERGE,
        json={"fromId": from_tool["id"], "toId": to_tool["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == to_tool["id"]
    assert result["recipeCount"] == 1

    assert (
        api_client.get(api_routes.organizers_tools_item_id(from_tool["id"]), headers=unique_user.token).status_code
        == 404
    )

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    tool_ids = [t["id"] for t in recipe["tools"]]
    assert to_tool["id"] in tool_ids
    assert from_tool["id"] not in tool_ids

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tools_item_id(to_tool["id"]), headers=unique_user.token)


def test_tool_merge_unknown_from_id_returns_404(api_client: TestClient, unique_user: TestUser):
    to_tool = _create_tool(api_client, unique_user)
    response = api_client.post(
        TOOLS_MERGE,
        json={"fromId": str(uuid.uuid4()), "toId": to_tool["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 404

    api_client.delete(api_routes.organizers_tools_item_id(to_tool["id"]), headers=unique_user.token)


def test_tool_merge_same_id_returns_400(api_client: TestClient, unique_user: TestUser):
    tool = _create_tool(api_client, unique_user)
    response = api_client.post(
        TOOLS_MERGE,
        json={"fromId": tool["id"], "toId": tool["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 400

    api_client.delete(api_routes.organizers_tools_item_id(tool["id"]), headers=unique_user.token)
