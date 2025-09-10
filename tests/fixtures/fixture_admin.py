from uuid import UUID

from pytest import fixture
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from mealie.core.config import get_app_settings
from mealie.repos.all_repositories import get_repositories
from tests import utils
from tests.utils import api_routes


@fixture(scope="session")
def admin_token(api_client: TestClient):
    settings = get_app_settings()

    form_data = {"username": settings._DEFAULT_EMAIL, "password": settings._DEFAULT_PASSWORD}
    return utils.login(form_data, api_client)


@fixture(scope="module")
def admin_user(session: Session, api_client: TestClient):
    settings = get_app_settings()

    form_data = {"username": settings._DEFAULT_EMAIL, "password": settings._DEFAULT_PASSWORD}

    token = utils.login(form_data, api_client)

    user_data = api_client.get(api_routes.users_self, headers=token).json()
    assert token is not None

    assert user_data.get("admin") is True
    assert (user_id := user_data.get("id")) is not None
    assert (group_id := user_data.get("groupId")) is not None
    assert (household_id := user_data.get("householdId")) is not None

    if not isinstance(user_id, UUID):
        user_id = UUID(user_id)
    if not isinstance(group_id, UUID):
        group_id = UUID(group_id)
    if not isinstance(household_id, UUID):
        household_id = UUID(household_id)

    try:
        yield utils.TestUser(
            _group_id=group_id,
            _household_id=household_id,
            user_id=user_id,
            password=settings._DEFAULT_PASSWORD,
            username=user_data.get("username"),
            full_name=user_data.get("fullName"),
            email=user_data.get("email"),
            token=token,
            repos=get_repositories(session, group_id=group_id, household_id=household_id),
        )
    finally:
        # TODO: Delete User after test
        pass
