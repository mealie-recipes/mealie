from fastapi.testclient import TestClient

from tests.utils.factories import user_registration_factory


class Routes:
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
