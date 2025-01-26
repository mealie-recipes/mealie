from datetime import UTC, datetime

from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_ownership_on_new_with_admin(api_client: TestClient, admin_user: TestUser):
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=admin_user.token)
    assert response.status_code == 201

    recipe = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=admin_user.token).json()

    assert recipe["userId"] == str(admin_user.user_id)
    assert recipe["groupId"] == str(admin_user.group_id)


def test_ownership_on_new_with_user(api_client: TestClient, g2_user: TestUser):
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=g2_user.token)
    assert response.status_code == 201

    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=g2_user.token)

    assert response.status_code == 200

    recipe = response.json()

    assert recipe["userId"] == str(g2_user.user_id)
    assert recipe["groupId"] == str(g2_user.group_id)


def test_get_all_only_includes_group_recipes(api_client: TestClient, unique_user: TestUser):
    for _ in range(5):
        recipe_name = random_string()
        response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=unique_user.token)

    response = api_client.get(api_routes.recipes, headers=unique_user.token)

    assert response.status_code == 200

    recipes = response.json()["items"]

    assert len(recipes) == 5

    for recipe in recipes:
        assert recipe["groupId"] == str(unique_user.group_id)
        assert recipe["userId"] == str(unique_user.user_id)


def test_unique_slug_by_group(api_client: TestClient, unique_user: TestUser, g2_user: TestUser) -> None:
    create_data = {"name": random_string()}

    response = api_client.post(api_routes.recipes, json=create_data, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.post(api_routes.recipes, json=create_data, headers=g2_user.token)
    assert response.status_code == 201

    # Try to create a recipe again with the same name and check that the name was incremented
    response = api_client.post(api_routes.recipes, json=create_data, headers=g2_user.token)
    assert response.status_code == 201
    assert response.json() == create_data["name"] + "-1"


def test_user_locked_recipe(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple

    # Setup Recipe
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=usr_1.token)
    assert response.status_code == 201

    # Get Recipe
    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=usr_1.token)
    assert response.status_code == 200
    recipe = response.json()

    # Lock Recipe
    recipe["settings"]["locked"] = True
    response = api_client.put(api_routes.recipes + f"/{recipe_name}", json=recipe, headers=usr_1.token)

    # Try To Update Recipe with User 2
    response = api_client.put(api_routes.recipes + f"/{recipe_name}", json=recipe, headers=usr_2.token)
    assert response.status_code == 403


def test_user_update_last_made(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple

    # Setup Recipe
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=usr_1.token)
    assert response.status_code == 201

    # Get Recipe
    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=usr_1.token)
    assert response.status_code == 200
    recipe = response.json()

    # Lock Recipe
    recipe["settings"]["locked"] = True
    response = api_client.put(api_routes.recipes + f"/{recipe_name}", json=recipe, headers=usr_1.token)

    # User 2 should be able to update the last made timestamp
    last_made_json = {"timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z")}
    response = api_client.patch(
        api_routes.recipes_slug_last_made(recipe_name), json=last_made_json, headers=usr_2.token
    )
    assert response.status_code == 200

    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=usr_1.token)
    assert response.status_code == 200
    recipe = response.json()
    assert recipe["lastMade"] == last_made_json["timestamp"]


def test_other_user_cant_lock_recipe(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple

    # Setup Recipe
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=usr_1.token)
    assert response.status_code == 201

    # Get Recipe
    response = api_client.get(api_routes.recipes + f"/{recipe_name}", headers=usr_2.token)
    assert response.status_code == 200
    recipe = response.json()

    # Lock Recipe
    recipe["settings"]["locked"] = True
    response = api_client.put(api_routes.recipes + f"/{recipe_name}", json=recipe, headers=usr_2.token)
    assert response.status_code == 403
