from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.utils import api_routes, random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_get_group_members(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    response = api_client.get(api_routes.groups_members, headers=unique_user.token)
    assert response.status_code == 200

    members = response.json()
    assert len(members) >= 2

    all_ids = [x["id"] for x in members]

    assert str(unique_user.user_id) in all_ids
    assert str(h2_user.user_id) in all_ids


def test_get_group_members_filtered(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    response = api_client.get(
        api_routes.groups_members, params={"householdId": h2_user.household_id}, headers=unique_user.token
    )
    assert response.status_code == 200

    members = response.json()
    assert len(members) >= 1

    all_ids = [x["id"] for x in members]

    assert str(unique_user.user_id) not in all_ids
    assert str(h2_user.user_id) in all_ids


def test_get_households(api_client: TestClient, admin_user: TestUser):
    households = [admin_user.repos.households.create({"name": random_string()}) for _ in range(5)]
    response = api_client.get(api_routes.groups_households, headers=admin_user.token)
    response_ids = [item["id"] for item in response.json()]
    for household in households:
        assert str(household.id) in response_ids


def test_get_households_filtered(unfiltered_database: AllRepositories, api_client: TestClient, admin_user: TestUser):
    group_1_id = admin_user.group_id
    group_2_id = str(unfiltered_database.groups.create({"name": random_string()}).id)

    group_1_households = [
        unfiltered_database.households.create({"name": random_string(), "group_id": group_1_id})
        for _ in range(random_int(2, 5))
    ]
    group_2_households = [
        unfiltered_database.households.create({"name": random_string(), "group_id": group_2_id})
        for _ in range(random_int(2, 5))
    ]

    response = api_client.get(api_routes.groups_households, headers=admin_user.token)
    response_ids = [item["id"] for item in response.json()]
    for household in group_1_households:
        assert str(household.id) in response_ids
    for household in group_2_households:
        assert str(household.id) not in response_ids
