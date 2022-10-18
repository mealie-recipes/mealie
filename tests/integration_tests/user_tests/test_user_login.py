import json

from fastapi.testclient import TestClient

from mealie.core.config import get_app_settings
from mealie.repos.repository_factory import AllRepositories
from mealie.services.user_services.user_service import UserService
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def test_failed_login(api_client: TestClient):
    settings = get_app_settings()

    form_data = {"username": settings.DEFAULT_EMAIL, "password": "WRONG_PASSWORD"}
    response = api_client.post(api_routes.auth_token, form_data)

    assert response.status_code == 401


def test_superuser_login(api_client: TestClient, admin_token):
    settings = get_app_settings()

    form_data = {"username": settings.DEFAULT_EMAIL, "password": settings.DEFAULT_PASSWORD}
    response = api_client.post(api_routes.auth_token, form_data)

    assert response.status_code == 200
    new_token = json.loads(response.text).get("access_token")

    response = api_client.get(api_routes.users_self, headers=admin_token)
    assert response.status_code == 200

    return {"Authorization": f"Bearer {new_token}"}


def test_user_token_refresh(api_client: TestClient, admin_user: TestUser):
    response = api_client.post(api_routes.auth_refresh, headers=admin_user.token)
    response = api_client.get(api_routes.users_self, headers=admin_user.token)
    assert response.status_code == 200


def test_user_lockout_after_bad_attemps(api_client: TestClient, unique_user: TestUser, database: AllRepositories):
    """
    if the user has more than 5 bad login attempts the user will be locked out for 4 hours
    This only applies if there is a user in the database with the same username
    """
    settings = get_app_settings()

    for _ in range(settings.SECURITY_MAX_LOGIN_ATTEMPTS):
        form_data = {"username": unique_user.email, "password": "bad_password"}
        response = api_client.post(api_routes.auth_token, form_data)

        assert response.status_code == 401

    valid_data = {"username": unique_user.email, "password": unique_user.password}
    response = api_client.post(api_routes.auth_token, valid_data)
    assert response.status_code == 423

    # Cleanup
    user_service = UserService(database)
    user = database.users.get_one(unique_user.user_id)
    user_service.unlock_user(user)
