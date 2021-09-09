import pytest
from fastapi.testclient import TestClient

from tests.utils.factories import user_registration_factory
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/groups/invitations"
    auth_token = "/api/auth/token"
    self = "/api/users/self"

    register = "/api/users/register"

    def item(item_id: int) -> str:
        return f"{Routes.base}/{item_id}"


@pytest.fixture(scope="function")
def invite(api_client: TestClient, unique_user: TestUser) -> None:
    # Test Creation
    r = api_client.post(Routes.base, json={"uses": 2}, headers=unique_user.token)
    assert r.status_code == 201
    invitation = r.json()
    return invitation["token"]


def test_get_all_invitation(api_client: TestClient, unique_user: TestUser, invite: str) -> None:
    # Get All Invites
    r = api_client.get(Routes.base, headers=unique_user.token)

    assert r.status_code == 200

    items = r.json()

    assert len(items) == 1

    for item in items:
        assert item["groupId"] == unique_user.group_id
        assert item["token"] == invite


def register_user(api_client, invite):
    # Test User can Join Group
    registration = user_registration_factory()
    registration.group = ""
    registration.group_token = invite

    response = api_client.post(Routes.register, json=registration.dict(by_alias=True))
    print(response.json())
    return registration, response


def test_group_invitation_link(api_client: TestClient, unique_user: TestUser, invite: str):
    registration, r = register_user(api_client, invite)
    assert r.status_code == 201

    # Login as new User
    form_data = {"username": registration.email, "password": registration.password}

    r = api_client.post(Routes.auth_token, form_data)
    assert r.status_code == 200
    token = r.json().get("access_token")
    assert token is not None

    # Check user Group is Same
    r = api_client.get(Routes.self, headers={"Authorization": f"Bearer {token}"})

    assert r.status_code == 200
    assert r.json()["groupId"] == unique_user.group_id


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
