from fastapi.testclient import TestClient

from mealie.schema.user.registration import CreateUserRegistration


class Routes:
    base = "/api/users/register"
    auth_token = "/api/auth/token"


def test_user_registration_new_group(api_client: TestClient):
    registration = CreateUserRegistration(
        group="New Group Name",
        email="email@email.com",
        username="fake-user-name",
        password="fake-password",
        password_confirm="fake-password",
        advanced=False,
        private=False,
    )

    response = api_client.post(Routes.base, json=registration.dict(by_alias=True))
    assert response.status_code == 201

    # Login
    form_data = {"username": "email@email.com", "password": "fake-password"}

    response = api_client.post(Routes.auth_token, form_data)
    assert response.status_code == 200
    token = response.json().get("access_token")

    assert token is not None
