import random

import pytest
import sqlalchemy
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.group_shopping_list import ShoppingListOut, ShoppingListSave
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/shopping/lists"

    def item(item_id: str) -> str:
        return f"{Routes.base}/{item_id}"

    def add_recipe(item_id: str, recipe_id: str) -> str:
        return f"{Routes.item(item_id)}/recipe/{recipe_id}"


@pytest.fixture(scope="function")
def shopping_lists(database: AllRepositories, unique_user: TestUser):

    models: list[ShoppingListOut] = []

    for _ in range(3):
        model = database.group_shopping_lists.create(
            ShoppingListSave(name=random_string(10), group_id=unique_user.group_id),
        )

        models.append(model)

    yield models

    for model in models:
        try:
            database.group_shopping_lists.delete(model.id)
        except sqlalchemy.exc.NoResultFound:  # Entry Deleted in Test
            pass


def test_shopping_lists_get_all(api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]):
    all_lists = api_client.get(Routes.base, headers=unique_user.token)
    assert all_lists.status_code == 200
    all_lists = all_lists.json()

    assert len(all_lists) == len(shopping_lists)

    known_ids = [str(model.id) for model in shopping_lists]

    for list_ in all_lists:
        assert list_["id"] in known_ids


def test_shopping_lists_create_one(api_client: TestClient, unique_user: TestUser):
    payload = {
        "name": random_string(10),
    }

    response = api_client.post(Routes.base, json=payload, headers=unique_user.token)
    assert response.status_code == 201

    response_list = response.json()

    assert response_list["name"] == payload["name"]
    assert response_list["groupId"] == str(unique_user.group_id)


def test_shopping_lists_get_one(api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]):
    shopping_list = shopping_lists[0]

    response = api_client.get(Routes.item(shopping_list.id), headers=unique_user.token)
    assert response.status_code == 200

    response_list = response.json()

    assert response_list["id"] == str(shopping_list.id)
    assert response_list["name"] == shopping_list.name
    assert response_list["groupId"] == str(shopping_list.group_id)


def test_shopping_lists_update_one(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    sample_list = random.choice(shopping_lists)

    payload = {
        "name": random_string(10),
        "id": str(sample_list.id),
        "groupId": str(sample_list.group_id),
        "listItems": [],
    }

    response = api_client.put(Routes.item(sample_list.id), json=payload, headers=unique_user.token)
    assert response.status_code == 200

    response_list = response.json()

    assert response_list["id"] == str(sample_list.id)
    assert response_list["name"] == payload["name"]
    assert response_list["groupId"] == str(sample_list.group_id)


def test_shopping_lists_delete_one(
    api_client: TestClient, unique_user: TestUser, shopping_lists: list[ShoppingListOut]
):
    sample_list = random.choice(shopping_lists)

    response = api_client.delete(Routes.item(sample_list.id), headers=unique_user.token)
    assert response.status_code == 200

    response = api_client.get(Routes.item(sample_list.id), headers=unique_user.token)
    assert response.status_code == 404


def test_shopping_lists_add_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
):
    sample_list = random.choice(shopping_lists)
    assert True


def test_shopping_lists_remove_recipe(
    api_client: TestClient,
    unique_user: TestUser,
    shopping_lists: list[ShoppingListOut],
):
    sample_list = random.choice(shopping_lists)
    assert True
