from uuid import uuid4

from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.utils.factories import random_bool
from tests.utils.fixture_schemas import TestUser


class Routes:
    self = "/api/groups/self"
    memebers = "/api/groups/members"
    permissions = "/api/groups/permissions"


def get_permissions_payload(user_id: str, can_manage=None) -> dict:
    return {
        "user_id": user_id,
        "can_manage": random_bool() if can_manage is None else can_manage,
        "can_invite": random_bool(),
        "can_organize": random_bool(),
    }


def test_get_group_members(api_client: TestClient, user_tuple: list[TestUser]):
    usr_1, usr_2 = user_tuple

    response = api_client.get(Routes.memebers, headers=usr_1.token)
    assert response.status_code == 200

    members = response.json()
    assert len(members) >= 2

    all_ids = [x["id"] for x in members]

    assert str(usr_1.user_id) in all_ids
    assert str(usr_2.user_id) in all_ids


def test_set_memeber_permissions(api_client: TestClient, user_tuple: list[TestUser], database: AllRepositories):
    usr_1, usr_2 = user_tuple

    # Set Acting User
    acting_user = database.users.get_one(usr_1.user_id)
    acting_user.can_manage = True
    database.users.update(acting_user.id, acting_user)

    payload = get_permissions_payload(str(usr_2.user_id))

    # Test
    response = api_client.put(Routes.permissions, json=payload, headers=usr_1.token)
    assert response.status_code == 200


def test_set_memeber_permissions_unauthorized(api_client: TestClient, unique_user: TestUser, database: AllRepositories):
    # Setup
    user = database.users.get_one(unique_user.user_id)
    user.can_manage = False
    database.users.update(user.id, user)

    payload = get_permissions_payload(str(user.id))
    payload = {
        "user_id": str(user.id),
        "can_manage": True,
        "can_invite": True,
        "can_organize": True,
    }

    # Test
    response = api_client.put(Routes.permissions, json=payload, headers=unique_user.token)
    assert response.status_code == 403


def test_set_memeber_permissions_other_group(
    api_client: TestClient,
    unique_user: TestUser,
    g2_user: TestUser,
    database: AllRepositories,
):
    user = database.users.get_one(unique_user.user_id)
    user.can_manage = True
    database.users.update(user.id, user)

    payload = get_permissions_payload(str(g2_user.user_id))
    response = api_client.put(Routes.permissions, json=payload, headers=unique_user.token)
    assert response.status_code == 403


def test_set_memeber_permissions_no_user(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
):
    user = database.users.get_one(unique_user.user_id)
    user.can_manage = True
    database.users.update(user.id, user)

    payload = get_permissions_payload(str(uuid4()))
    response = api_client.put(Routes.permissions, json=payload, headers=unique_user.token)
    assert response.status_code == 404
