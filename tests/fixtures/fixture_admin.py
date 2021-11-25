import requests
from pytest import fixture
from starlette.testclient import TestClient

from mealie.core.config import get_app_settings
from tests import utils


@fixture(scope="session")
def admin_token(api_client: requests, api_routes: utils.AppRoutes):
    settings = get_app_settings()

    form_data = {"username": "changeme@email.com", "password": settings.DEFAULT_PASSWORD}
    return utils.login(form_data, api_client, api_routes)


@fixture(scope="session")
def admin_user(api_client: TestClient, api_routes: utils.AppRoutes):
    settings = get_app_settings()

    form_data = {"username": "changeme@email.com", "password": settings.DEFAULT_PASSWORD}

    token = utils.login(form_data, api_client, api_routes)

    user_data = api_client.get(api_routes.users_self, headers=token).json()
    assert token is not None

    assert user_data.get("admin") is True
    assert user_data.get("groupId") is not None
    assert user_data.get("id") is not None

    try:
        yield utils.TestUser(
            group_id=user_data.get("groupId"),
            user_id=user_data.get("id"),
            email=user_data.get("email"),
            token=token,
        )
    finally:
        # TODO: Delete User after test
        pass
