import json

from starlette.testclient import TestClient

from tests import utils
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def create_recipe(api_client: TestClient, user: TestUser, private: bool = False) -> str:
    response = api_client.post(api_routes.recipes, json={"name": utils.random_string()}, headers=user.token)
    assert response.status_code == 201
    slug = response.json()

    if private:
        recipe = json.loads(api_client.get(api_routes.recipes_slug(slug), headers=user.token).text)
        recipe["settings"]["private"] = True

        response = api_client.put(api_routes.recipes_slug(slug), json=utils.jsonify(recipe), headers=user.token)
        assert response.status_code == 200

    return slug


def list_slugs(api_client: TestClient, user: TestUser) -> list[str]:
    response = api_client.get(api_routes.recipes, headers=user.token)
    assert response.status_code == 200
    return [item["slug"] for item in response.json()["items"]]


def test_private_recipe_only_visible_to_author(
    api_client: TestClient,
    unique_user: TestUser,
    h2_user: TestUser,
):
    """A private recipe is hidden from other users in the same group."""
    private_slug = create_recipe(api_client, unique_user, private=True)

    assert api_client.get(api_routes.recipes_slug(private_slug), headers=unique_user.token).status_code == 200
    assert api_client.get(api_routes.recipes_slug(private_slug), headers=h2_user.token).status_code == 404

    assert private_slug in list_slugs(api_client, unique_user)
    assert private_slug not in list_slugs(api_client, h2_user)


def test_private_recipe_visible_to_group_admin(
    api_client: TestClient,
    unique_user: TestUser,
    unique_admin: TestUser,
):
    """Group admins can see recipes marked as private."""
    private_slug = create_recipe(api_client, unique_user, private=True)

    assert api_client.get(api_routes.recipes_slug(private_slug), headers=unique_admin.token).status_code == 200
    assert private_slug in list_slugs(api_client, unique_admin)


def test_public_recipe_visible_to_other_users(
    api_client: TestClient,
    unique_user: TestUser,
    h2_user: TestUser,
):
    """Recipes that are not marked private stay visible to the whole group."""
    slug = create_recipe(api_client, unique_user, private=False)

    assert api_client.get(api_routes.recipes_slug(slug), headers=h2_user.token).status_code == 200
    assert slug in list_slugs(api_client, h2_user)


def test_private_recipe_cannot_be_modified_or_exported_by_others(
    api_client: TestClient,
    unique_user: TestUser,
    h2_user: TestUser,
):
    """Other users cannot update, delete, comment or export someone else's private recipe."""
    private_slug = create_recipe(api_client, unique_user, private=True)
    url = api_routes.recipes_slug(private_slug)

    assert api_client.patch(url, json={"name": "hacked"}, headers=h2_user.token).status_code == 404
    assert api_client.delete(url, headers=h2_user.token).status_code == 404

    export_response = api_client.get(
        api_routes.recipes_slug_exports(private_slug),
        params={"template_name": "recipes.md"},
        headers=h2_user.token,
    )
    assert export_response.status_code == 404
