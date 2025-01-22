from uuid import uuid4

from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_bool
from tests.utils.fixture_schemas import TestUser


def get_permissions_payload(user_id: str, can_manage=None, can_manage_household=None) -> dict:
    return {
        "user_id": user_id,
        "can_manage": random_bool() if can_manage is None else can_manage,
        "can_manage_household": random_bool(),
        "can_invite": random_bool(),
        "can_organize": random_bool(),
    }


def test_set_member_permissions(api_client: TestClient, user_tuple: list[TestUser]):
    usr_1, usr_2 = user_tuple

    # Set Acting User
    acting_user = usr_1.repos.users.get_one(usr_1.user_id)
    assert acting_user
    acting_user.can_manage = True
    usr_1.repos.users.update(acting_user.id, acting_user)

    payload = get_permissions_payload(str(usr_2.user_id))

    # Test
    response = api_client.put(api_routes.households_permissions, json=payload, headers=usr_1.token)
    assert response.status_code == 200


def test_set_member_permissions_unauthorized(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos

    # Setup
    user = database.users.get_one(unique_user.user_id)
    assert user
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
    response = api_client.put(api_routes.households_permissions, json=payload, headers=unique_user.token)
    assert response.status_code == 403


def test_set_member_permissions_other_household(
    api_client: TestClient,
    unique_user: TestUser,
    h2_user: TestUser,
):
    database = unique_user.repos

    user = database.users.get_one(unique_user.user_id)
    assert user
    user.can_manage = True
    database.users.update(user.id, user)

    payload = get_permissions_payload(str(h2_user.user_id))
    response = api_client.put(api_routes.households_permissions, json=payload, headers=unique_user.token)
    assert response.status_code == 403


def test_set_member_permissions_no_user(
    api_client: TestClient,
    unique_user: TestUser,
):
    database = unique_user.repos

    user = database.users.get_one(unique_user.user_id)
    assert user
    user.can_manage = True
    database.users.update(user.id, user)

    payload = get_permissions_payload(str(uuid4()))
    response = api_client.put(api_routes.households_permissions, json=payload, headers=unique_user.token)
    assert response.status_code == 404


def test_set_own_permissions(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos

    user = database.users.get_one(unique_user.user_id)
    assert user
    user.can_manage = True
    database.users.update(user.id, user)

    form = {"user_id": str(unique_user.user_id), "canOrganize": not user.can_organize}
    response = api_client.put(api_routes.households_permissions, json=form, headers=unique_user.token)
    assert response.status_code == 403
