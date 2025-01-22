import pytest
from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_email, random_int, random_string
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("use_admin_user", [True, False])
def test_get_all_users_admin(request: pytest.FixtureRequest, api_client: TestClient, use_admin_user: bool):
    user: TestUser
    if use_admin_user:
        user = request.getfixturevalue("admin_user")
    else:
        user = request.getfixturevalue("unique_user")

    database = user.repos
    user_ids: set[str] = set()
    for _ in range(random_int(2, 5)):
        group = database.groups.create({"name": random_string()})
        household = database.households.create({"name": random_string(), "group_id": group.id})
        for _ in range(random_int(2, 5)):
            new_user = database.users.create(
                {
                    "username": random_string(),
                    "email": random_email(),
                    "group": group.name,
                    "household": household.name,
                    "full_name": random_string(),
                    "password": random_string(),
                    "admin": False,
                }
            )
            user_ids.add(str(new_user.id))

    response = api_client.get(api_routes.admin_users, params={"perPage": -1}, headers=user.token)
    if not use_admin_user:
        assert response.status_code == 403
        return

    assert response.status_code == 200

    # assert all users from all groups are returned
    response_user_ids = {user["id"] for user in response.json()["items"]}
    for user_id in user_ids:
        assert user_id in response_user_ids


def test_user_update(api_client: TestClient, unique_user: TestUser, admin_user: TestUser):
    response = api_client.get(api_routes.users_self, headers=unique_user.token)
    user = response.json()

    # valid request without updates
    response = api_client.put(api_routes.users_item_id(unique_user.user_id), json=user, headers=unique_user.token)
    assert response.status_code == 200

    # valid request with updates
    tmp_user = user.copy()
    tmp_user["email"] = random_email()
    tmp_user["full_name"] = random_string()
    response = api_client.put(api_routes.users_item_id(unique_user.user_id), json=tmp_user, headers=unique_user.token)
    assert response.status_code == 200

    # test user attempting to update another user
    form = {"email": admin_user.email, "full_name": admin_user.full_name}
    response = api_client.put(api_routes.users_item_id(admin_user.user_id), json=form, headers=unique_user.token)
    assert response.status_code == 403

    # test user attempting permission changes
    permissions = ["canInvite", "canManage", "canManageHousehold", "canOrganize", "advanced", "admin"]
    for permission in permissions:
        tmp_user = user.copy()
        tmp_user[permission] = not user[permission]
        response = api_client.put(api_routes.users_item_id(unique_user.user_id), json=form, headers=unique_user.token)
        assert response.status_code == 403

    # test user attempting to change group
    tmp_user = user.copy()
    tmp_user["group"] = random_string()
    response = api_client.put(api_routes.users_item_id(unique_user.user_id), json=tmp_user, headers=unique_user.token)
    assert response.status_code == 403

    # test user attempting to change household
    tmp_user = user.copy()
    tmp_user["household"] = random_string()
    response = api_client.put(api_routes.users_item_id(unique_user.user_id), json=tmp_user, headers=unique_user.token)
    assert response.status_code == 403


def test_admin_updates(api_client: TestClient, admin_user: TestUser, unique_user: TestUser):
    response = api_client.get(api_routes.users_item_id(unique_user.user_id), headers=admin_user.token)
    user = response.json()
    response = api_client.get(api_routes.users_item_id(admin_user.user_id), headers=admin_user.token)
    admin = response.json()

    # admin updating themselves
    tmp_user = admin.copy()
    tmp_user["fullName"] = random_string()
    response = api_client.put(api_routes.users_item_id(admin_user.user_id), json=tmp_user, headers=admin_user.token)
    assert response.status_code == 200

    # admin updating another user via the normal user route
    tmp_user = user.copy()
    tmp_user["fullName"] = random_string()
    response = api_client.put(api_routes.users_item_id(unique_user.user_id), json=tmp_user, headers=admin_user.token)
    assert response.status_code == 403

    # admin updating their own permissions
    permissions = ["canInvite", "canManage", "canManageHousehold", "canOrganize", "admin"]
    for permission in permissions:
        tmp_user = admin.copy()
        tmp_user[permission] = not admin[permission]
        response = api_client.put(api_routes.users_item_id(admin_user.user_id), json=tmp_user, headers=admin_user.token)
        assert response.status_code == 403
