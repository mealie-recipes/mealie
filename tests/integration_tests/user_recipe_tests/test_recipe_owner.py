from fastapi.testclient import TestClient

from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/recipes"
    user = "/api/users/self"


def test_ownership_on_new_with_admin(api_client: TestClient, admin_user: TestUser):
    recipe_name = random_string()
    response = api_client.post(Routes.base, json={"name": recipe_name}, headers=admin_user.token)
    assert response.status_code == 201

    recipe = api_client.get(Routes.base + f"/{recipe_name}", headers=admin_user.token).json()

    assert recipe["userId"] == admin_user.user_id
    assert recipe["groupId"] == admin_user.group_id


def test_ownership_on_new_with_user(api_client: TestClient, g2_user: TestUser):
    recipe_name = random_string()
    response = api_client.post(Routes.base, json={"name": recipe_name}, headers=g2_user.token)
    assert response.status_code == 201

    response = api_client.get(Routes.base + f"/{recipe_name}", headers=g2_user.token)

    assert response.status_code == 200

    recipe = response.json()

    assert recipe["userId"] == g2_user.user_id
    assert recipe["groupId"] == g2_user.group_id


def test_get_all_only_includes_group_recipes(api_client: TestClient, unique_user: TestUser):
    for _ in range(5):
        recipe_name = random_string()
        response = api_client.post(Routes.base, json={"name": recipe_name}, headers=unique_user.token)

    response = api_client.get(Routes.base, headers=unique_user.token)

    assert response.status_code == 200

    recipes = response.json()

    assert len(recipes) == 5

    for recipe in recipes:
        assert recipe["groupId"] == unique_user.group_id
        assert recipe["userId"] == unique_user.user_id


def test_unique_slug_by_group(api_client: TestClient, unique_user: TestUser, g2_user: TestUser) -> None:
    create_data = {"name": random_string()}

    response = api_client.post(Routes.base, json=create_data, headers=unique_user.token)
    assert response.status_code == 201

    response = api_client.post(Routes.base, json=create_data, headers=g2_user.token)
    assert response.status_code == 201

    # Try to create a recipe again with the same name and check that the name was incremented
    response = api_client.post(Routes.base, json=create_data, headers=g2_user.token)
    assert response.status_code == 201
    assert response.json() == create_data["name"] + "-1"


def test_user_locked_recipe(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple

    # Setup Recipe
    recipe_name = random_string()
    response = api_client.post(Routes.base, json={"name": recipe_name}, headers=usr_1.token)
    assert response.status_code == 201

    # Get Recipe
    response = api_client.get(Routes.base + f"/{recipe_name}", headers=usr_1.token)
    assert response.status_code == 200
    recipe = response.json()

    # Lock Recipe
    recipe["settings"]["locked"] = True
    response = api_client.put(Routes.base + f"/{recipe_name}", json=recipe, headers=usr_1.token)

    # Try To Update Recipe with User 2
    response = api_client.put(Routes.base + f"/{recipe_name}", json=recipe, headers=usr_2.token)
    assert response.status_code == 403


def test_other_user_cant_lock_recipe(api_client: TestClient, user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple

    # Setup Recipe
    recipe_name = random_string()
    response = api_client.post(Routes.base, json={"name": recipe_name}, headers=usr_1.token)
    assert response.status_code == 201

    # Get Recipe
    response = api_client.get(Routes.base + f"/{recipe_name}", headers=usr_2.token)
    assert response.status_code == 200
    recipe = response.json()

    # Lock Recipe
    recipe["settings"]["locked"] = True
    response = api_client.put(Routes.base + f"/{recipe_name}", json=recipe, headers=usr_2.token)
    assert response.status_code == 403
