from fastapi.testclient import TestClient

from tests.utils.factories import user_registration_factory


class Routes:
    self = "/api/users/self"
    base = "/api/users/register"
    auth_token = "/api/auth/token"


def test_user_registration_new_group(api_client: TestClient):
    registration = user_registration_factory()

    response = api_client.post(Routes.base, json=registration.dict(by_alias=True))
    assert response.status_code == 201

    # Login
    form_data = {"username": registration.email, "password": registration.password}

    response = api_client.post(Routes.auth_token, form_data)
    assert response.status_code == 200
    token = response.json().get("access_token")

    assert token is not None


def test_new_user_group_permissions(api_client: TestClient):
    registration = user_registration_factory()

    response = api_client.post(Routes.base, json=registration.dict(by_alias=True))
    assert response.status_code == 201

    # Login
    form_data = {"username": registration.email, "password": registration.password}

    response = api_client.post(Routes.auth_token, form_data)
    assert response.status_code == 200
    token = response.json().get("access_token")

    assert token is not None

    # Get User

    headers = {"Authorization": f"Bearer {token}"}
    response = api_client.get(Routes.self, headers=headers)

    assert response.status_code == 200
    user = response.json()

    assert user.get("canInvite") is True
    assert user.get("canManage") is True
    assert user.get("canOrganize") is True
