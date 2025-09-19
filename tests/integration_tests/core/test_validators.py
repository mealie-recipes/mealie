from dataclasses import dataclass
from uuid import UUID

from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import Recipe
from tests.utils import api_routes, random_string
from tests.utils.fixture_schemas import TestUser


@dataclass()
class SimpleCase:
    value: str
    is_valid: bool


def test_validators_username(api_client: TestClient, unique_user: TestUser):
    users = [
        SimpleCase(value=unique_user.username, is_valid=False),
        SimpleCase(value=random_string(), is_valid=True),
    ]

    for user in users:
        response = api_client.get(api_routes.validators_user_name + "?name=" + user.value)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["valid"] == user.is_valid


def test_validators_email(api_client: TestClient, unique_user: TestUser):
    emails = [
        SimpleCase(value=unique_user.email, is_valid=False),
        SimpleCase(value=f"{random_string()}@example.com", is_valid=True),
    ]

    for user in emails:
        response = api_client.get(api_routes.validators_user_email + "?email=" + user.value)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["valid"] == user.is_valid


def test_validators_group_name(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos
    group = database.groups.get_one(unique_user.group_id)
    assert group

    groups = [
        SimpleCase(value=group.name, is_valid=False),
        SimpleCase(value=random_string(), is_valid=True),
    ]

    for user in groups:
        response = api_client.get(api_routes.validators_group + "?name=" + user.value)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["valid"] == user.is_valid


@dataclass(slots=True)
class RecipeValidators:
    name: str
    group: UUID | str
    is_valid: bool


def test_validators_recipe(api_client: TestClient, random_recipe: Recipe):
    recipes = [
        RecipeValidators(name=random_recipe.name or "", group=random_recipe.group_id, is_valid=False),
        RecipeValidators(name=random_string(), group=random_recipe.group_id, is_valid=True),
        RecipeValidators(name=random_string(), group=random_recipe.group_id, is_valid=True),
    ]

    for recipe in recipes:
        response = api_client.get(api_routes.validators_recipe + f"?group_id={recipe.group}&name={recipe.name}")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["valid"] == recipe.is_valid
