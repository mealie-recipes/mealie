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
    (routes.RoutesCategory),
    (routes.RoutesTags),
    (routes.RoutesTools),
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
    (routes.RoutesCategory, {"name": random_string(10)}),
    (routes.RoutesTags, {"name": random_string(10)}),
    (routes.RoutesTools, {"name": random_string(10), "onHand": random_bool()}),
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
    (routes.RoutesCategory, recipe_keys.recipe_category),
    (routes.RoutesTags, "tags"),
    (routes.RoutesTools, "tools"),
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
    response = api_client.post(routes.RoutesRecipe.base, json=recipe_data, headers=unique_user.token)
    slug = response.json()
    assert response.status_code == 201

    # Get Recipe Data
    response = api_client.get(routes.RoutesRecipe.item(slug), headers=unique_user.token)
    as_json = response.json()
    as_json[recipe_key] = [{"id": item["id"], "name": item["name"], "slug": item["slug"]}]

    # Update Recipe
    response = api_client.put(routes.RoutesRecipe.item(slug), json=as_json, headers=unique_user.token)
    assert response.status_code == 200

    # Get Recipe Data
    response = api_client.get(routes.RoutesRecipe.item(slug), headers=unique_user.token)
    as_json = response.json()
    assert as_json[recipe_key][0]["slug"] == item["slug"]

    # Cleanup
    response = api_client.delete(routes.RoutesRecipe.item(slug), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.delete(route.item(item["id"]), headers=unique_user.token)
    assert response.status_code == 200
