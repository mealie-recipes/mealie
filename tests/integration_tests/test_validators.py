from fastapi.testclient import TestClient

from mealie.db.db_setup import create_session
from mealie.schema.recipe.recipe import Recipe
from tests.utils.fixture_schemas import TestUser


class Routes:
    user = "/api/validators/user"
    recipe = "/api/validators/recipe"


def test_validators_user(api_client: TestClient, unique_user: TestUser):
    session = create_session()

    # Test existing user
    response = api_client.get(Routes.user + f"/{unique_user.username}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["valid"] == False

    # Test non-existing user
    response = api_client.get(Routes.user + f"/{unique_user.username}2")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["valid"] == True

    session.close()


def test_validators_recipe(api_client: TestClient, random_recipe: Recipe):
    session = create_session()

    # Test existing user
    response = api_client.get(Routes.recipe + f"/{random_recipe.group_id}/{random_recipe.slug}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["valid"] == False

    # Test non-existing user
    response = api_client.get(Routes.recipe + f"/{random_recipe.group_id}/{random_recipe.slug}-test")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["valid"] == True

    session.close()
