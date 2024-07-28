from fastapi.testclient import TestClient

from tests.utils import api_routes
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
