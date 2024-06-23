import pytest
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.utils import TestUser, api_routes
from tests.utils.factories import random_email, random_int, random_string


@pytest.mark.parametrize("use_admin_user", [True, False])
def test_get_all_users_admin(
    request: pytest.FixtureRequest, database: AllRepositories, api_client: TestClient, use_admin_user: bool
):
    user: TestUser
    if use_admin_user:
        user = request.getfixturevalue("admin_user")
    else:
        user = request.getfixturevalue("unique_user")

    user_ids: set[str] = set()
    for _ in range(random_int(2, 5)):
        group = database.groups.create({"name": random_string()})
        for _ in range(random_int(2, 5)):
            new_user = database.users.create(
                {
                    "username": random_string(),
                    "email": random_email(),
                    "group": group.name,
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


@pytest.mark.parametrize("use_admin_user", [True, False])
def test_get_all_group_users(
    request: pytest.FixtureRequest, database: AllRepositories, api_client: TestClient, use_admin_user: bool
):
    user: TestUser
    if use_admin_user:
        user = request.getfixturevalue("admin_user")
    else:
        user = request.getfixturevalue("unique_user")

    other_group_user_ids: set[str] = set()
    for _ in range(random_int(2, 5)):
        group = database.groups.create({"name": random_string()})
        for _ in range(random_int(2, 5)):
            new_user = database.users.create(
                {
                    "username": random_string(),
                    "email": random_email(),
                    "group": group.name,
                    "full_name": random_string(),
                    "password": random_string(),
                    "admin": False,
                }
            )
            other_group_user_ids.add(str(new_user.id))

    user_group = database.groups.get_by_slug_or_id(user.group_id)
    assert user_group
    same_group_user_ids: set[str] = {user.user_id}
    for _ in range(random_int(2, 5)):
        new_user = database.users.create(
            {
                "username": random_string(),
                "email": random_email(),
                "group": user_group.name,
                "full_name": random_string(),
                "password": random_string(),
                "admin": False,
            }
        )
        same_group_user_ids.add(str(new_user.id))

    response = api_client.get(api_routes.users_group_users, params={"perPage": -1}, headers=user.token)
    assert response.status_code == 200
    response_user_ids = {user["id"] for user in response.json()["items"]}

    # assert only users from the same group are returned
    for user_id in other_group_user_ids:
        assert user_id not in response_user_ids
    for user_id in same_group_user_ids:
        assert user_id in response_user_ids
