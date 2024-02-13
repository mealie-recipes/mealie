from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import user_registration_factory


def test_user_registration_new_group(api_client: TestClient):
    registration = user_registration_factory()

    response = api_client.post(api_routes.users_register, json=registration.model_dump(by_alias=True))
    assert response.status_code == 201

    # Login
    form_data = {"username": registration.email, "password": registration.password}

    response = api_client.post(api_routes.auth_token, data=form_data)
    assert response.status_code == 200
    token = response.json().get("access_token")

    assert token is not None


def test_new_user_group_permissions(api_client: TestClient):
    registration = user_registration_factory()

    response = api_client.post(api_routes.users_register, json=registration.model_dump(by_alias=True))
    assert response.status_code == 201

    # Login
    form_data = {"username": registration.email, "password": registration.password}

    response = api_client.post(api_routes.auth_token, data=form_data)
    assert response.status_code == 200
    token = response.json().get("access_token")

    assert token is not None

    # Get User

    headers = {"Authorization": f"Bearer {token}"}
    response = api_client.get(api_routes.users_self, headers=headers)

    assert response.status_code == 200
    user = response.json()

    assert user.get("canInvite") is True
    assert user.get("canManage") is True
    assert user.get("canOrganize") is True
