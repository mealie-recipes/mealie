import random
from dataclasses import dataclass
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.schema.cookbook.cookbook import ReadCookBook, SaveCookBook
from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def get_page_data(group_id: UUID | str, household_id: UUID4 | str):
    name_and_slug = random_string(10)
    return {
        "name": name_and_slug,
        "slug": name_and_slug,
        "description": "",
        "position": 0,
        "categories": [],
        "group_id": str(group_id),
        "household_id": str(household_id),
    }


@dataclass
class TestCookbook:
    id: UUID4
    slug: str
    name: str
    data: dict


@pytest.fixture(scope="function")
def cookbooks(unique_user: TestUser) -> list[TestCookbook]:
    database = unique_user.repos

    data: list[ReadCookBook] = []
    yield_data: list[TestCookbook] = []
    for _ in range(3):
        cb = database.cookbooks.create(SaveCookBook(**get_page_data(unique_user.group_id, unique_user.household_id)))
        data.append(cb)
        yield_data.append(TestCookbook(id=cb.id, slug=cb.slug, name=cb.name, data=cb.model_dump()))

    yield yield_data

    for cb in yield_data:
        try:
            database.cookbooks.delete(cb.id)
        except Exception:
            pass


def test_create_cookbook(api_client: TestClient, unique_user: TestUser):
    page_data = get_page_data(unique_user.group_id, unique_user.household_id)
    response = api_client.post(api_routes.households_cookbooks, json=page_data, headers=unique_user.token)
    assert response.status_code == 201


def test_read_cookbook(api_client: TestClient, unique_user: TestUser, cookbooks: list[TestCookbook]):
    sample = random.choice(cookbooks)
    response = api_client.get(api_routes.households_cookbooks_item_id(sample.id), headers=unique_user.token)
    assert response.status_code == 200

    page_data = response.json()

    assert page_data["id"] == str(sample.id)
    assert page_data["slug"] == sample.slug
    assert page_data["name"] == sample.name
    assert page_data["groupId"] == str(unique_user.group_id)


def test_update_cookbook(api_client: TestClient, unique_user: TestUser, cookbooks: list[TestCookbook]):
    cookbook = random.choice(cookbooks)

    update_data = get_page_data(unique_user.group_id, unique_user.household_id)

    update_data["name"] = random_string(10)

    response = api_client.put(
        api_routes.households_cookbooks_item_id(cookbook.id), json=update_data, headers=unique_user.token
    )
    assert response.status_code == 200

    response = api_client.get(api_routes.households_cookbooks_item_id(cookbook.id), headers=unique_user.token)
    assert response.status_code == 200

    page_data = response.json()
    assert page_data["name"] == update_data["name"]
    assert page_data["slug"] == update_data["name"]


def test_update_cookbooks_many(api_client: TestClient, unique_user: TestUser, cookbooks: list[TestCookbook]):
    pages = [x.data for x in cookbooks]

    reverse_order = sorted(pages, key=lambda x: x["position"], reverse=True)
    for x, page in enumerate(reverse_order):
        page["position"] = x
        page["group_id"] = str(unique_user.group_id)

    response = api_client.put(
        api_routes.households_cookbooks, json=utils.jsonify(reverse_order), headers=unique_user.token
    )
    assert response.status_code == 200

    response = api_client.get(api_routes.households_cookbooks, headers=unique_user.token)
    assert response.status_code == 200

    known_ids = [x.id for x in cookbooks]

    server_ids = [x["id"] for x in response.json()["items"]]

    for know in known_ids:  # Hacky check, because other tests don't cleanup after themselves :(
        assert str(know) in server_ids


def test_delete_cookbook(api_client: TestClient, unique_user: TestUser, cookbooks: list[TestCookbook]):
    sample = random.choice(cookbooks)
    response = api_client.delete(api_routes.households_cookbooks_item_id(sample.id), headers=unique_user.token)

    assert response.status_code == 200

    response = api_client.get(api_routes.households_cookbooks_item_id(sample.slug), headers=unique_user.token)
    assert response.status_code == 404
