"""Integration tests for the Tag Groups feature.

Tests cover:
- Tag group CRUD (create, read, update, delete, get by slug)
- Tag group assignment: assign tag_group_id to a tag, verify it's returned
- Cascade delete: deleting a group sets tag_group_id to null (ungrouped)
- Recipe filter: ?tagGroups=<id> (OR mode) and ?tagGroups=<id>&requireAllTagGroups=true (AND mode)
"""
import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

TAG_GROUPS_BASE = "/api/organizers/tag-groups"
TAGS_BASE = "/api/organizers/tags"


def tag_groups_item(item_id: str) -> str:
    return f"{TAG_GROUPS_BASE}/{item_id}"


def tag_groups_slug(slug: str) -> str:
    return f"{TAG_GROUPS_BASE}/slug/{slug}"


def tags_item(item_id: str) -> str:
    return f"{TAGS_BASE}/{item_id}"


# ==============================================================================
# Tag Group CRUD


def test_tag_group_create_and_read(api_client: TestClient, unique_user: TestUser) -> None:
    name = random_string(10)
    data = {"name": name, "color": "#ff0000", "position": 5}

    response = api_client.post(TAG_GROUPS_BASE, json=data, headers=unique_user.token)
    assert response.status_code == 201

    created = response.json()
    group_id = created["id"]
    assert created["name"] == name
    assert created["color"] == "#ff0000"
    assert created["position"] == 5
    assert "slug" in created

    # Read back by ID
    response = api_client.get(tag_groups_item(group_id), headers=unique_user.token)
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == group_id
    assert item["name"] == name

    # Cleanup
    api_client.delete(tag_groups_item(group_id), headers=unique_user.token)


def test_tag_group_update(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.post(
        TAG_GROUPS_BASE,
        json={"name": random_string(10), "color": "#aabbcc", "position": 0},
        headers=unique_user.token,
    )
    assert response.status_code == 201
    group_id = response.json()["id"]

    new_name = random_string(10)
    response = api_client.put(
        tag_groups_item(group_id),
        json={"name": new_name, "color": "#112233", "position": 3},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == new_name
    assert updated["color"] == "#112233"
    assert updated["position"] == 3

    api_client.delete(tag_groups_item(group_id), headers=unique_user.token)


def test_tag_group_delete(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.post(
        TAG_GROUPS_BASE,
        json={"name": random_string(10)},
        headers=unique_user.token,
    )
    assert response.status_code == 201
    group_id = response.json()["id"]

    response = api_client.delete(tag_groups_item(group_id), headers=unique_user.token)
    assert response.status_code == 204

    response = api_client.get(tag_groups_item(group_id), headers=unique_user.token)
    assert response.status_code == 404


def test_tag_group_get_by_slug(api_client: TestClient, unique_user: TestUser) -> None:
    name = random_string(10)
    response = api_client.post(TAG_GROUPS_BASE, json={"name": name}, headers=unique_user.token)
    assert response.status_code == 201
    created = response.json()
    group_id = created["id"]
    slug = created["slug"]

    response = api_client.get(tag_groups_slug(slug), headers=unique_user.token)
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == group_id
    assert item["slug"] == slug

    api_client.delete(tag_groups_item(group_id), headers=unique_user.token)


def test_tag_group_list(api_client: TestClient, unique_user: TestUser) -> None:
    created_ids = []
    for _ in range(3):
        response = api_client.post(
            TAG_GROUPS_BASE, json={"name": random_string(10)}, headers=unique_user.token
        )
        assert response.status_code == 201
        created_ids.append(response.json()["id"])

    response = api_client.get(TAG_GROUPS_BASE, headers=unique_user.token)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    returned_ids = {item["id"] for item in data["items"]}
    for gid in created_ids:
        assert gid in returned_ids

    for gid in created_ids:
        api_client.delete(tag_groups_item(gid), headers=unique_user.token)


def test_tag_group_summary_includes_tags(api_client: TestClient, unique_user: TestUser) -> None:
    """GET /tag-groups/{id} returns the tags belonging to the group."""
    group_resp = api_client.post(
        TAG_GROUPS_BASE, json={"name": random_string(10)}, headers=unique_user.token
    )
    assert group_resp.status_code == 201
    group_id = group_resp.json()["id"]

    # Create a tag and assign it to the group
    tag_resp = api_client.post(TAGS_BASE, json={"name": random_string(10)}, headers=unique_user.token)
    assert tag_resp.status_code == 201
    tag = tag_resp.json()
    tag_id = tag["id"]

    # Update the tag with tagGroupId
    update_payload = {**tag, "tagGroupId": group_id}
    response = api_client.put(tags_item(tag_id), json=update_payload, headers=unique_user.token)
    assert response.status_code == 200

    # Fetch the group summary
    response = api_client.get(tag_groups_item(group_id), headers=unique_user.token)
    assert response.status_code == 200
    summary = response.json()
    tag_ids_in_group = [t["id"] for t in summary.get("tags", [])]
    assert tag_id in tag_ids_in_group

    # Cleanup
    api_client.delete(tags_item(tag_id), headers=unique_user.token)
    api_client.delete(tag_groups_item(group_id), headers=unique_user.token)


# ==============================================================================
# Tag group assignment


def test_tag_group_id_saved_and_returned(api_client: TestClient, unique_user: TestUser) -> None:
    """Assigning a tagGroupId to a tag is persisted and returned by GET."""
    group_resp = api_client.post(
        TAG_GROUPS_BASE, json={"name": random_string(10)}, headers=unique_user.token
    )
    assert group_resp.status_code == 201
    group_id = group_resp.json()["id"]

    tag_resp = api_client.post(TAGS_BASE, json={"name": random_string(10)}, headers=unique_user.token)
    assert tag_resp.status_code == 201
    tag = tag_resp.json()
    tag_id = tag["id"]

    # Update tag: assign group
    update_payload = {**tag, "tagGroupId": group_id}
    put_resp = api_client.put(tags_item(tag_id), json=update_payload, headers=unique_user.token)
    assert put_resp.status_code == 200
    assert put_resp.json().get("tagGroupId") == group_id

    # Verify GET returns tagGroupId
    get_resp = api_client.get(tags_item(tag_id), headers=unique_user.token)
    assert get_resp.status_code == 200
    assert get_resp.json().get("tagGroupId") == group_id

    # Cleanup
    api_client.delete(tags_item(tag_id), headers=unique_user.token)
    api_client.delete(tag_groups_item(group_id), headers=unique_user.token)


def test_tag_group_id_can_be_cleared(api_client: TestClient, unique_user: TestUser) -> None:
    """Setting tagGroupId to null removes the tag from its group."""
    group_resp = api_client.post(
        TAG_GROUPS_BASE, json={"name": random_string(10)}, headers=unique_user.token
    )
    assert group_resp.status_code == 201
    group_id = group_resp.json()["id"]

    tag_resp = api_client.post(TAGS_BASE, json={"name": random_string(10)}, headers=unique_user.token)
    assert tag_resp.status_code == 201
    tag = tag_resp.json()
    tag_id = tag["id"]

    # Assign to group
    api_client.put(tags_item(tag_id), json={**tag, "tagGroupId": group_id}, headers=unique_user.token)

    # Clear group assignment
    put_resp = api_client.put(tags_item(tag_id), json={**tag, "tagGroupId": None}, headers=unique_user.token)
    assert put_resp.status_code == 200

    get_resp = api_client.get(tags_item(tag_id), headers=unique_user.token)
    assert get_resp.status_code == 200
    assert get_resp.json().get("tagGroupId") is None

    # Cleanup
    api_client.delete(tags_item(tag_id), headers=unique_user.token)
    api_client.delete(tag_groups_item(group_id), headers=unique_user.token)


# ==============================================================================
# Cascade delete


def test_cascade_delete_group_ungroups_tags(api_client: TestClient, unique_user: TestUser) -> None:
    """Deleting a tag group sets tag_group_id to NULL on all its tags."""
    group_resp = api_client.post(
        TAG_GROUPS_BASE, json={"name": random_string(10)}, headers=unique_user.token
    )
    assert group_resp.status_code == 201
    group_id = group_resp.json()["id"]

    # Create two tags and assign them to the group
    tag_ids = []
    for _ in range(2):
        tag_resp = api_client.post(TAGS_BASE, json={"name": random_string(10)}, headers=unique_user.token)
        assert tag_resp.status_code == 201
        tag = tag_resp.json()
        tag_id = tag["id"]
        api_client.put(tags_item(tag_id), json={**tag, "tagGroupId": group_id}, headers=unique_user.token)
        tag_ids.append(tag_id)

    # Delete the group
    del_resp = api_client.delete(tag_groups_item(group_id), headers=unique_user.token)
    assert del_resp.status_code == 204

    # Tags must still exist but with tagGroupId == null
    for tag_id in tag_ids:
        get_resp = api_client.get(tags_item(tag_id), headers=unique_user.token)
        assert get_resp.status_code == 200
        assert get_resp.json().get("tagGroupId") is None

    # Cleanup tags
    for tag_id in tag_ids:
        api_client.delete(tags_item(tag_id), headers=unique_user.token)


# ==============================================================================
# Recipe filter


def _create_recipe_with_tags(
    api_client: TestClient,
    user: TestUser,
    tag_ids: list[str],
    group_id: str,
) -> str:
    """Helper: create a recipe and assign the given tags to it. Returns the slug."""
    # Fetch the actual tag data (name/slug) so the recipe update links correctly
    tags_payload = []
    for tid in tag_ids:
        tag_resp = api_client.get(tags_item(tid), headers=user.token)
        assert tag_resp.status_code == 200
        t = tag_resp.json()
        tags_payload.append({"id": t["id"], "groupId": t["groupId"], "name": t["name"], "slug": t["slug"]})

    recipe_resp = api_client.post(
        api_routes.recipes, json={"name": random_string(10)}, headers=user.token
    )
    assert recipe_resp.status_code == 201
    slug = recipe_resp.json()

    recipe_resp = api_client.get(api_routes.recipes_slug(slug), headers=user.token)
    assert recipe_resp.status_code == 200
    recipe = recipe_resp.json()

    recipe["tags"] = tags_payload
    put_resp = api_client.put(api_routes.recipes_slug(slug), json=recipe, headers=user.token)
    assert put_resp.status_code == 200

    return slug


def test_recipe_filter_by_tag_group_or_mode(api_client: TestClient, unique_user: TestUser) -> None:
    """GET /api/recipes?tagGroups=<id> returns only recipes that have at least one tag from the group."""
    group_resp = api_client.post(
        TAG_GROUPS_BASE, json={"name": random_string(10)}, headers=unique_user.token
    )
    assert group_resp.status_code == 201
    group_id = group_resp.json()["id"]

    # Create two tags in the group
    tag_ids = []
    for _ in range(2):
        tag_resp = api_client.post(TAGS_BASE, json={"name": random_string(10)}, headers=unique_user.token)
        assert tag_resp.status_code == 201
        tag = tag_resp.json()
        tag_id = tag["id"]
        api_client.put(tags_item(tag_id), json={**tag, "tagGroupId": group_id}, headers=unique_user.token)
        tag_ids.append(tag_id)

    # Recipe A: has tag[0] (in group)
    # Recipe B: has tag[1] (in group)
    # Recipe C: no tags from this group
    slug_a = _create_recipe_with_tags(api_client, unique_user, [tag_ids[0]], unique_user.group_id)
    slug_b = _create_recipe_with_tags(api_client, unique_user, [tag_ids[1]], unique_user.group_id)
    slug_c_resp = api_client.post(
        api_routes.recipes, json={"name": random_string(10)}, headers=unique_user.token
    )
    assert slug_c_resp.status_code == 201
    slug_c = slug_c_resp.json()

    # Filter by tag group — OR mode (default)
    filter_resp = api_client.get(
        api_routes.recipes,
        params={"tagGroups": group_id, "perPage": -1},
        headers=unique_user.token,
    )
    assert filter_resp.status_code == 200
    result = filter_resp.json()
    returned_slugs = {r["slug"] for r in result["items"]}

    assert slug_a in returned_slugs
    assert slug_b in returned_slugs
    assert slug_c not in returned_slugs

    # Cleanup
    for slug in [slug_a, slug_b, slug_c]:
        api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    for tag_id in tag_ids:
        api_client.delete(tags_item(tag_id), headers=unique_user.token)
    api_client.delete(tag_groups_item(group_id), headers=unique_user.token)


def test_recipe_filter_by_multiple_tag_groups_and_mode(
    api_client: TestClient, unique_user: TestUser
) -> None:
    """?tagGroups=A&tagGroups=B&requireAllTagGroups=true returns recipes with tags from BOTH groups."""
    group_ids = []
    tag_ids_per_group: list[list[str]] = []

    for _ in range(2):
        group_resp = api_client.post(
            TAG_GROUPS_BASE, json={"name": random_string(10)}, headers=unique_user.token
        )
        assert group_resp.status_code == 201
        group_id = group_resp.json()["id"]
        group_ids.append(group_id)

        tag_resp = api_client.post(TAGS_BASE, json={"name": random_string(10)}, headers=unique_user.token)
        assert tag_resp.status_code == 201
        tag = tag_resp.json()
        tag_id = tag["id"]
        api_client.put(tags_item(tag_id), json={**tag, "tagGroupId": group_id}, headers=unique_user.token)
        tag_ids_per_group.append([tag_id])

    # Recipe A: tags from both groups
    slug_both = _create_recipe_with_tags(
        api_client, unique_user,
        [tag_ids_per_group[0][0], tag_ids_per_group[1][0]],
        unique_user.group_id,
    )
    # Recipe B: tag from group[0] only
    slug_one = _create_recipe_with_tags(
        api_client, unique_user, [tag_ids_per_group[0][0]], unique_user.group_id
    )

    # AND mode: only slug_both should appear
    filter_resp = api_client.get(
        api_routes.recipes,
        params={
            "tagGroups": group_ids,
            "requireAllTagGroups": "true",
            "perPage": -1,
        },
        headers=unique_user.token,
    )
    assert filter_resp.status_code == 200
    result = filter_resp.json()
    returned_slugs = {r["slug"] for r in result["items"]}

    assert slug_both in returned_slugs
    assert slug_one not in returned_slugs

    # OR mode: both slugs should appear
    or_resp = api_client.get(
        api_routes.recipes,
        params={"tagGroups": group_ids, "perPage": -1},
        headers=unique_user.token,
    )
    assert or_resp.status_code == 200
    or_slugs = {r["slug"] for r in or_resp.json()["items"]}
    assert slug_both in or_slugs
    assert slug_one in or_slugs

    # Cleanup
    for slug in [slug_both, slug_one]:
        api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    for tag_list in tag_ids_per_group:
        for tag_id in tag_list:
            api_client.delete(tags_item(tag_id), headers=unique_user.token)
    for group_id in group_ids:
        api_client.delete(tag_groups_item(group_id), headers=unique_user.token)
