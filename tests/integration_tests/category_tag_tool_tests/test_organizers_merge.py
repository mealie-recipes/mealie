"""
Integration tests for:
- recipe_count field on GET /organizers/tags and GET /organizers/categories
- POST /organizers/tags/merge
- POST /organizers/categories/merge
"""

from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TAGS_MERGE = "/api/organizers/tags/merge"
CATEGORIES_MERGE = "/api/organizers/categories/merge"


def _create_tag(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(api_routes.organizers_tags, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _create_category(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(api_routes.organizers_categories, json={"name": random_string(10)}, headers=user.token)
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


def _set_recipe_categories(api_client: TestClient, user: TestUser, slug: str, categories: list[dict]) -> None:
    response = api_client.get(api_routes.recipes_slug(slug), headers=user.token)
    assert response.status_code == 200
    body = response.json()
    body["recipeCategory"] = [
        {"id": c["id"], "groupId": user.group_id, "name": c["name"], "slug": c["slug"]} for c in categories
    ]
    response = api_client.put(api_routes.recipes_slug(slug), json=body, headers=user.token)
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Tags — recipe_count
# ---------------------------------------------------------------------------


def test_tag_list_includes_recipe_count_for_tagged_recipe(api_client: TestClient, unique_user: TestUser):
    tag = _create_tag(api_client, unique_user)
    slug = _create_recipe(api_client, unique_user)
    _set_recipe_tags(api_client, unique_user, slug, [tag])

    response = api_client.get(api_routes.organizers_tags, headers=unique_user.token)
    assert response.status_code == 200
    items = response.json()["items"]
    match = next((t for t in items if t["id"] == tag["id"]), None)
    assert match is not None
    assert match["recipeCount"] == 1

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token)


def test_tag_list_recipe_count_is_zero_for_empty_tag(api_client: TestClient, unique_user: TestUser):
    tag = _create_tag(api_client, unique_user)

    response = api_client.get(api_routes.organizers_tags, headers=unique_user.token)
    assert response.status_code == 200
    items = response.json()["items"]
    match = next((t for t in items if t["id"] == tag["id"]), None)
    assert match is not None
    assert match["recipeCount"] == 0

    api_client.delete(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Tags — merge
# ---------------------------------------------------------------------------


def test_tag_merge_moves_exclusive_recipes_to_target(api_client: TestClient, unique_user: TestUser):
    """Recipes belonging only to from_tag are reassigned to to_tag."""
    from_tag = _create_tag(api_client, unique_user)
    to_tag = _create_tag(api_client, unique_user)

    slug1 = _create_recipe(api_client, unique_user)
    slug2 = _create_recipe(api_client, unique_user)
    _set_recipe_tags(api_client, unique_user, slug1, [from_tag])
    _set_recipe_tags(api_client, unique_user, slug2, [to_tag])

    response = api_client.post(
        TAGS_MERGE,
        json={"fromId": from_tag["id"], "toId": to_tag["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == to_tag["id"]
    assert result["recipeCount"] == 2

    # from_tag must be deleted
    assert (
        api_client.get(api_routes.organizers_tags_item_id(from_tag["id"]), headers=unique_user.token).status_code == 404
    )

    # both recipes must carry to_tag
    for slug in (slug1, slug2):
        recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
        tag_ids = [t["id"] for t in recipe["tags"]]
        assert to_tag["id"] in tag_ids
        assert from_tag["id"] not in tag_ids

    api_client.delete(api_routes.recipes_slug(slug1), headers=unique_user.token)
    api_client.delete(api_routes.recipes_slug(slug2), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(to_tag["id"]), headers=unique_user.token)


def test_tag_merge_overlap_does_not_violate_unique_constraint(api_client: TestClient, unique_user: TestUser):
    """A recipe that already has both from_tag and to_tag must not cause a DB unique-constraint error."""
    from_tag = _create_tag(api_client, unique_user)
    to_tag = _create_tag(api_client, unique_user)

    slug = _create_recipe(api_client, unique_user)
    _set_recipe_tags(api_client, unique_user, slug, [from_tag, to_tag])

    response = api_client.post(
        TAGS_MERGE,
        json={"fromId": from_tag["id"], "toId": to_tag["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == to_tag["id"]
    assert result["recipeCount"] == 1

    # from_tag must be deleted
    assert (
        api_client.get(api_routes.organizers_tags_item_id(from_tag["id"]), headers=unique_user.token).status_code == 404
    )

    # recipe must have exactly to_tag, not from_tag
    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    tag_ids = [t["id"] for t in recipe["tags"]]
    assert to_tag["id"] in tag_ids
    assert from_tag["id"] not in tag_ids

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(to_tag["id"]), headers=unique_user.token)


def test_tag_merge_unknown_from_id_returns_404(api_client: TestClient, unique_user: TestUser):
    import uuid

    to_tag = _create_tag(api_client, unique_user)
    response = api_client.post(
        TAGS_MERGE,
        json={"fromId": str(uuid.uuid4()), "toId": to_tag["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 404

    api_client.delete(api_routes.organizers_tags_item_id(to_tag["id"]), headers=unique_user.token)


def test_tag_merge_same_id_returns_400(api_client: TestClient, unique_user: TestUser):
    tag = _create_tag(api_client, unique_user)
    response = api_client.post(
        TAGS_MERGE,
        json={"fromId": tag["id"], "toId": tag["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 400

    api_client.delete(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Categories — recipe_count
# ---------------------------------------------------------------------------


def test_category_list_includes_recipe_count_for_categorised_recipe(api_client: TestClient, unique_user: TestUser):
    category = _create_category(api_client, unique_user)
    slug = _create_recipe(api_client, unique_user)
    _set_recipe_categories(api_client, unique_user, slug, [category])

    response = api_client.get(api_routes.organizers_categories, headers=unique_user.token)
    assert response.status_code == 200
    items = response.json()["items"]
    match = next((c for c in items if c["id"] == category["id"]), None)
    assert match is not None
    assert match["recipeCount"] == 1

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.organizers_categories_item_id(category["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Categories — merge
# ---------------------------------------------------------------------------


def test_category_merge_moves_exclusive_recipes_to_target(api_client: TestClient, unique_user: TestUser):
    from_cat = _create_category(api_client, unique_user)
    to_cat = _create_category(api_client, unique_user)

    slug1 = _create_recipe(api_client, unique_user)
    slug2 = _create_recipe(api_client, unique_user)
    _set_recipe_categories(api_client, unique_user, slug1, [from_cat])
    _set_recipe_categories(api_client, unique_user, slug2, [to_cat])

    response = api_client.post(
        CATEGORIES_MERGE,
        json={"fromId": from_cat["id"], "toId": to_cat["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == to_cat["id"]
    assert result["recipeCount"] == 2

    assert (
        api_client.get(api_routes.organizers_categories_item_id(from_cat["id"]), headers=unique_user.token).status_code
        == 404
    )

    for slug in (slug1, slug2):
        recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
        cat_ids = [c["id"] for c in recipe["recipeCategory"]]
        assert to_cat["id"] in cat_ids
        assert from_cat["id"] not in cat_ids

    api_client.delete(api_routes.recipes_slug(slug1), headers=unique_user.token)
    api_client.delete(api_routes.recipes_slug(slug2), headers=unique_user.token)
    api_client.delete(api_routes.organizers_categories_item_id(to_cat["id"]), headers=unique_user.token)


def test_category_merge_overlap_does_not_violate_unique_constraint(api_client: TestClient, unique_user: TestUser):
    from_cat = _create_category(api_client, unique_user)
    to_cat = _create_category(api_client, unique_user)

    slug = _create_recipe(api_client, unique_user)
    _set_recipe_categories(api_client, unique_user, slug, [from_cat, to_cat])

    response = api_client.post(
        CATEGORIES_MERGE,
        json={"fromId": from_cat["id"], "toId": to_cat["id"]},
        headers=unique_user.token,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == to_cat["id"]
    assert result["recipeCount"] == 1

    assert (
        api_client.get(api_routes.organizers_categories_item_id(from_cat["id"]), headers=unique_user.token).status_code
        == 404
    )

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    cat_ids = [c["id"] for c in recipe["recipeCategory"]]
    assert to_cat["id"] in cat_ids
    assert from_cat["id"] not in cat_ids

    api_client.delete(api_routes.recipes_slug(slug), headers=unique_user.token)
    api_client.delete(api_routes.organizers_categories_item_id(to_cat["id"]), headers=unique_user.token)
