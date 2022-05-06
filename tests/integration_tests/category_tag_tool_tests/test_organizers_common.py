import pytest
from fastapi.testclient import TestClient

from mealie.schema.static import recipe_keys
from tests.utils import routes
from tests.utils.factories import random_bool, random_string
from tests.utils.fixture_schemas import TestUser

# Test IDs to be used to identify the test cases - order matters!
test_ids = [
    "category",
    "tags",
    "tools",
]

organizer_routes = [
    (routes.organizers.Categories),
    (routes.organizers.Tags),
    (routes.organizers.Tools),
]


@pytest.mark.parametrize("route", organizer_routes, ids=test_ids)
def test_organizers_create_read(api_client: TestClient, unique_user: TestUser, route: routes.RoutesBase):
    data = {"name": random_string(10)}

    response = api_client.post(route.base, json=data, headers=unique_user.token)
    assert response.status_code == 201

    item_id = response.json()["id"]

    response = api_client.get(route.item(item_id), headers=unique_user.token)
    assert response.status_code == 200

    item = response.json()

    assert item["id"] == item_id
    assert item["name"] == data["name"]
    assert item["slug"] == data["name"]

    response = api_client.delete(route.item(item_id), headers=unique_user.token)
    assert response.status_code == 200


update_data = [
    (routes.organizers.Categories, {"name": random_string(10)}),
    (routes.organizers.Tags, {"name": random_string(10)}),
    (routes.organizers.Tools, {"name": random_string(10), "onHand": random_bool()}),
]


@pytest.mark.parametrize("route, update_data", update_data, ids=test_ids)
def test_organizer_update(
    api_client: TestClient,
    unique_user: TestUser,
    route: routes.RoutesBase,
    update_data: dict,
):
    data = {"name": random_string(10)}

    response = api_client.post(route.base, json=data, headers=unique_user.token)
    assert response.status_code == 201
    item = response.json()
    item_id = item["id"]

    # Update the item if the key is presetn in the update_data
    for key in update_data:
        if key in item:
            item[key] = update_data[key]

    response = api_client.put(route.item(item_id), json=item, headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(route.item(item_id), headers=unique_user.token)

    item = response.json()

    for key, value in update_data.items():
        if key in item:
            assert item[key] == value


@pytest.mark.parametrize("route", organizer_routes, ids=test_ids)
def test_organizer_delete(
    api_client: TestClient,
    unique_user: TestUser,
    route: routes.RoutesBase,
):
    data = {"name": random_string(10)}

    response = api_client.post(route.base, json=data, headers=unique_user.token)
    assert response.status_code == 201
    item = response.json()
    item_id = item["id"]

    response = api_client.delete(route.item(item_id), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(route.item(item_id), headers=unique_user.token)
    assert response.status_code == 404


association_data = [
    (routes.organizers.Categories, recipe_keys.recipe_category),
    (routes.organizers.Tags, "tags"),
    (routes.organizers.Tools, "tools"),
]


@pytest.mark.parametrize("route, recipe_key", association_data, ids=test_ids)
def test_organizer_association(
    api_client: TestClient,
    unique_user: TestUser,
    route: routes.RoutesBase,
    recipe_key: str,
):
    data = {"name": random_string(10)}

    # Setup Organizer
    response = api_client.post(route.base, json=data, headers=unique_user.token)
    assert response.status_code == 201
    item = response.json()

    # Setup Recipe
    recipe_data = {"name": random_string(10)}
    response = api_client.post(routes.recipes.Recipe.base, json=recipe_data, headers=unique_user.token)
    slug = response.json()
    assert response.status_code == 201

    # Get Recipe Data
    response = api_client.get(routes.recipes.Recipe.item(slug), headers=unique_user.token)
    as_json = response.json()
    as_json[recipe_key] = [
        {"id": item["id"], "group_id": unique_user.group_id, "name": item["name"], "slug": item["slug"]}
    ]

    # Update Recipe
    response = api_client.put(routes.recipes.Recipe.item(slug), json=as_json, headers=unique_user.token)
    assert response.status_code == 200

    # Get Recipe Data
    response = api_client.get(routes.recipes.Recipe.item(slug), headers=unique_user.token)
    as_json = response.json()
    assert as_json[recipe_key][0]["slug"] == item["slug"]

    # Cleanup
    response = api_client.delete(routes.recipes.Recipe.item(slug), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.delete(route.item(item["id"]), headers=unique_user.token)
    assert response.status_code == 200


@pytest.mark.parametrize("route, recipe_key", association_data, ids=test_ids)
def test_organizer_get_by_slug(
    api_client: TestClient,
    unique_user: TestUser,
    route: routes.organizers.RoutesOrganizerBase,
    recipe_key: str,
):
    # Create Organizer
    data = {"name": random_string(10)}
    response = api_client.post(route.base, json=data, headers=unique_user.token)
    assert response.status_code == 201
    item = response.json()

    # Create 10 Recipes
    recipe_slugs = []

    for _ in range(10):
        # Setup Recipe
        recipe_data = {"name": random_string(10)}
        response = api_client.post(routes.recipes.Recipe.base, json=recipe_data, headers=unique_user.token)
        assert response.status_code == 201
        slug = response.json()
        recipe_slugs.append(slug)

    # Associate 10 Recipes to Organizer
    for slug in recipe_slugs:
        response = api_client.get(routes.recipes.Recipe.item(slug), headers=unique_user.token)
        as_json = response.json()
        as_json[recipe_key] = [
            {"id": item["id"], "group_id": unique_user.group_id, "name": item["name"], "slug": item["slug"]}
        ]

        response = api_client.put(routes.recipes.Recipe.item(slug), json=as_json, headers=unique_user.token)
        assert response.status_code == 200

    # Get Organizer by Slug
    response = api_client.get(route.slug(item["slug"]), headers=unique_user.token)
    assert response.status_code == 200

    as_json = response.json()
    assert as_json["slug"] == item["slug"]

    recipes = as_json["recipes"]

    # Check if Organizer is returned with 10 RecipeSummary
    assert len(recipes) == len(recipe_slugs)

    for recipe in recipes:
        assert recipe["slug"] in recipe_slugs
