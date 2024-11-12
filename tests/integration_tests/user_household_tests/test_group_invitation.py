from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import user_registration_factory
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(scope="function")
def invite(api_client: TestClient, unique_user: TestUser) -> None:
    # Test Creation
    r = api_client.post(api_routes.households_invitations, json={"uses": 2}, headers=unique_user.token)
    assert r.status_code == 201
    invitation = r.json()
    return invitation["token"]


def test_get_all_invitation(api_client: TestClient, unique_user: TestUser, invite: str) -> None:
    # Get All Invites
    r = api_client.get(api_routes.households_invitations, headers=unique_user.token)

    assert r.status_code == 200

    items = r.json()

    assert len(items) == 1

    for item in items:
        assert item["groupId"] == unique_user.group_id
        assert item["householdId"] == unique_user.household_id
        assert item["token"] == invite


def test_create_invitation(api_client: TestClient, unique_user: TestUser) -> None:
    # Create invitation for the same group as user
    r = api_client.post(api_routes.households_invitations, json={"uses": 1}, headers=unique_user.token)
    assert r.status_code == 201

    # Create invitation for other group as user
    body = {
        "uses": 1,
        "groupId": str(uuid4()),
        "householdId": str(uuid4()),
    }
    r = api_client.post(api_routes.households_invitations, json=body, headers=unique_user.token)
    assert r.status_code == 403


def register_user(api_client: TestClient, invite: str):
    # Test User can Join Group
    registration = user_registration_factory()
    registration.group = ""
    registration.household = ""
    registration.group_token = invite

    response = api_client.post(api_routes.users_register, json=registration.model_dump(by_alias=True))
    return registration, response


def test_group_invitation_link(api_client: TestClient, unique_user: TestUser, invite: str):
    registration, r = register_user(api_client, invite)
    assert r.status_code == 201

    # Login as new User
    form_data = {"username": registration.email, "password": registration.password}

    r = api_client.post(api_routes.auth_token, data=form_data)
    assert r.status_code == 200
    token = r.json().get("access_token")
    assert token is not None

    # Check user Group and Household match
    r = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {token}"})

    assert r.status_code == 200
    assert r.json()["groupId"] == unique_user.group_id
    assert r.json()["householdId"] == unique_user.household_id


def test_group_invitation_delete_after_uses(api_client: TestClient, invite: str) -> None:
    # Register First User
    _, r = register_user(api_client, invite)
    assert r.status_code == 201

    # Register Second User
    _, r = register_user(api_client, invite)
    assert r.status_code == 201

    # Check Group Invitation is Deleted
    _, r = register_user(api_client, invite)
    assert r.status_code == 400
