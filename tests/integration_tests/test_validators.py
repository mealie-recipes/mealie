from dataclasses import dataclass
from uuid import UUID

from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe
from tests.utils import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/validators"

    @staticmethod
    def username(username: str):
        return f"{Routes.base}/user/name?name={username}"

    @staticmethod
    def email(email: str):
        return f"{Routes.base}/user/email?email={email}"

    @staticmethod
    def group(group_name: str):
        return f"{Routes.base}/group?name={group_name}"

    @staticmethod
    def recipe(group_id, name) -> str:
        return f"{Routes.base}/recipe?group_id={group_id}&name={name}"


@dataclass(slots=True)
class SimpleCase:
    value: str
    is_valid: bool


def test_validators_username(api_client: TestClient, unique_user: TestUser):
    users = [
        SimpleCase(value=unique_user.username, is_valid=False),
        SimpleCase(value=random_string(), is_valid=True),
    ]

    for user in users:
        response = api_client.get(Routes.username(user.value))
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["valid"] == user.is_valid


def test_validators_email(api_client: TestClient, unique_user: TestUser):
    emails = [
        SimpleCase(value=unique_user.email, is_valid=False),
        SimpleCase(value=f"{random_string()}@email.com", is_valid=True),
    ]

    for user in emails:
        response = api_client.get(Routes.email(user.value))
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["valid"] == user.is_valid


def test_validators_group_name(api_client: TestClient, unique_user: TestUser, database: AllRepositories):
    group = database.groups.get_one(unique_user.group_id)

    groups = [
        SimpleCase(value=group.name, is_valid=False),
        SimpleCase(value=random_string(), is_valid=True),
    ]

    for user in groups:
        response = api_client.get(Routes.group(user.value))
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
        RecipeValidators(name=random_recipe.name, group=random_recipe.group_id, is_valid=False),
        RecipeValidators(name=random_string(), group=random_recipe.group_id, is_valid=True),
        RecipeValidators(name=random_string(), group=random_recipe.group_id, is_valid=True),
    ]

    for recipe in recipes:
        response = api_client.get(Routes.recipe(recipe.group, recipe.name))
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["valid"] == recipe.is_valid
