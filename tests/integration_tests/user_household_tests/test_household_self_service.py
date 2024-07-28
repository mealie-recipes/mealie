from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def test_get_household_members(api_client: TestClient, user_tuple: list[TestUser], h2_user: TestUser):
    usr_1, usr_2 = user_tuple

    response = api_client.get(api_routes.households_members, headers=usr_1.token)
    assert response.status_code == 200

    members = response.json()
    assert len(members) >= 2

    all_ids = [x["id"] for x in members]

    assert str(usr_1.user_id) in all_ids
    assert str(usr_2.user_id) in all_ids
    assert str(h2_user.user_id) not in all_ids
