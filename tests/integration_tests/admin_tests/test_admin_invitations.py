import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(scope="function")
def invite_same_group(api_client: TestClient, admin_user: TestUser) -> None:
    # Test User Creation without parameters (same group as admin)
    r = api_client.post(api_routes.households_invitations, json={"uses": 2}, headers=admin_user.token)
    assert r.status_code == 201
    invitation = r.json()
    return invitation["token"]


@pytest.fixture(scope="function")
def invite_other_group(api_client: TestClient, admin_user: TestUser) -> None:
    # Test User Creation with parameters (other group admin)
    body = {
        "uses": 1,
        "groupId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "householdId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    }
    r = api_client.post(api_routes.households_invitations, json=body, headers=admin_user.token)
    assert r.status_code == 201
    invitation = r.json()
    return invitation


def test_admin_get_all(
    api_client: TestClient, admin_user: TestUser, invite_same_group: str, invite_other_group: dict
) -> None:
    # Get All invitations
    r = api_client.get(api_routes.admin_invitations, headers=admin_user.token)

    assert r.status_code == 200
    items = r.json()

    assert len(items) == 2

    assert items[0]["groupId"] == invite_other_group["groupId"]
    assert items[0]["householdId"] == invite_other_group["householdId"]
    assert items[0]["token"] == invite_other_group["token"]

    assert items[1]["groupId"] == admin_user.group_id
    assert items[1]["householdId"] == admin_user.household_id
    assert items[1]["token"] == invite_same_group

    # Get invitations with query_filter on groupId
    r = api_client.get(
        api_routes.admin_invitations,
        headers=admin_user.token,
        params=f"queryFilter=groupId={admin_user.group_id}",
    )
    items = r.json()

    assert len(items) == 1
    assert items[0]["groupId"] == admin_user.group_id
