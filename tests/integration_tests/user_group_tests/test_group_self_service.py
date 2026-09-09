import random

import pytest
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.utils import api_routes, random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_get_group_members(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    response = api_client.get(api_routes.groups_members, params={"perPage": -1}, headers=unique_user.token)
    assert response.status_code == 200

    members = response.json()["items"]
    assert len(members) >= 2

    all_ids = [x["id"] for x in members]

    assert str(unique_user.user_id) in all_ids
    assert str(h2_user.user_id) in all_ids


@pytest.mark.parametrize("query", ["id", "username"])
def test_get_group_member(api_client: TestClient, unique_user: TestUser, h2_user: TestUser, query: str):
    if query == "id":
        param = str(h2_user.user_id)
    else:
        param = h2_user.username

    response = api_client.get(api_routes.groups_members_username_or_id(param), headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["id"] == str(h2_user.user_id)


def test_get_group_member_not_found(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(api_routes.groups_members_username_or_id(random_string()), headers=unique_user.token)
    assert response.status_code == 404


def test_get_households(api_client: TestClient, unique_user: TestUser):
    households = [unique_user.repos.households.create({"name": random_string()}) for _ in range(5)]
    response = api_client.get(api_routes.groups_households, headers=unique_user.token)
    response_ids = [item["id"] for item in response.json()["items"]]
    for household in households:
        assert str(household.id) in response_ids


def test_get_households_filtered(unfiltered_database: AllRepositories, api_client: TestClient, unique_user: TestUser):
    group_1_id = unique_user.group_id
    group_2_id = str(unfiltered_database.groups.create({"name": random_string()}).id)

    group_1_households = [
        unfiltered_database.households.create({"name": random_string(), "group_id": group_1_id})
        for _ in range(random_int(2, 5))
    ]
    group_2_households = [
        unfiltered_database.households.create({"name": random_string(), "group_id": group_2_id})
        for _ in range(random_int(2, 5))
    ]

    response = api_client.get(api_routes.groups_households, headers=unique_user.token)
    response_ids = [item["id"] for item in response.json()["items"]]
    for household in group_1_households:
        assert str(household.id) in response_ids
    for household in group_2_households:
        assert str(household.id) not in response_ids


def test_get_one_household(api_client: TestClient, unique_user: TestUser):
    households = [unique_user.repos.households.create({"name": random_string()}) for _ in range(5)]
    household = random.choice(households)

    response = api_client.get(api_routes.groups_households_household_slug(household.slug), headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["id"] == str(household.id)


def test_get_one_household_not_found(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(api_routes.groups_households_household_slug(random_string()), headers=unique_user.token)
    assert response.status_code == 404
