import json

from fastapi.testclient import TestClient

from mealie.db.db_setup import create_session
from mealie.services.user_services.password_reset_service import PasswordResetService
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


class Routes:
    base = "/api/users/reset-password"

    login = "/api/auth/token"
    self = "/api/users/self"


def test_password_reset(api_client: TestClient, unique_user: TestUser):
    session = create_session()

    service = PasswordResetService(session)
    token = service.generate_reset_token(unique_user.email)

    new_password = random_string(15)

    payload = {
        "token": token.token,
        "email": unique_user.email,
        "password": new_password,
        "passwordConfirm": new_password,
    }

    # Test successful password reset
    response = api_client.post(Routes.base, json=payload)
    assert response.status_code == 200

    # Test Login
    form_data = {"username": unique_user.email, "password": new_password}
    response = api_client.post(Routes.login, form_data)
    assert response.status_code == 200

    # Test Token
    new_token = json.loads(response.text).get("access_token")
    token = {"Authorization": f"Bearer {new_token}"}
    response = api_client.get(Routes.self, headers=token)
    assert response.status_code == 200

    session.close()

    # Test successful password reset
    response = api_client.post(Routes.base, json=payload)
    assert response.status_code == 400
