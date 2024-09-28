import pytest
from fastapi.testclient import TestClient

from tests.utils import TestUser, api_routes
from tests.utils.factories import random_email, random_int, random_string


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
