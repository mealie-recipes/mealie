import json
from collections.abc import Generator
from uuid import UUID

from pytest import fixture
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from mealie.db.db_setup import session_context
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories
from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_string


def build_unique_user(session: Session, group: str, api_client: TestClient) -> utils.TestUser:
    group = group or random_string(12)

    registration = utils.user_registration_factory()
    response = api_client.post("/api/users/register", json=registration.model_dump(by_alias=True))
    assert response.status_code == 201

    form_data = {"username": registration.username, "password": registration.password}

    token = utils.login(form_data, api_client)

    user_data = api_client.get(api_routes.users_self, headers=token).json()
    assert token is not None

    user_id = user_data.get("id")
    group_id = user_data.get("groupId")
    household_id = user_data.get("householdId")

    if not isinstance(user_id, UUID):
        user_id = UUID(user_id)
    if not isinstance(group_id, UUID):
        group_id = UUID(group_id)
    if not isinstance(household_id, UUID):
        household_id = UUID(household_id)

    return utils.TestUser(
        _group_id=group_id,
        _household_id=household_id,
        user_id=user_id,
        email=user_data.get("email"),
        username=user_data.get("username"),
        full_name=user_data.get("fullName"),
        password=registration.password,
        token=token,
        repos=get_repositories(session, group_id=group_id, household_id=household_id),
    )


@fixture(scope="module")
def h2_user(session: Session, admin_token, api_client: TestClient, unique_user: utils.TestUser):
    """Another user in the same group as `unique_user`, but in a different household"""
    group = api_client.get(api_routes.groups_self, headers=unique_user.token).json()
    household_name = random_string(12)
    api_client.post(
        api_routes.admin_households,
        json={
            "name": household_name,
            "groupId": group["id"],
        },
        headers=admin_token,
    )

    user_data = {
        "fullName": utils.random_string(),
        "username": utils.random_string(),
        "email": utils.random_email(),
        "password": "useruser",
        "group": group["name"],
        "household": household_name,
        "admin": False,
        "tokens": [],
    }
    response = api_client.post(api_routes.users, json=user_data, headers=admin_token)
    assert response.status_code == 201

    # Log in as this user
    form_data = {"username": user_data["email"], "password": "useruser"}
    token = utils.login(form_data, api_client)

    self_response = api_client.get(api_routes.users_self, headers=token)
    assert self_response.status_code == 200

    data = json.loads(self_response.text)
    user_id = data["id"]
    household_id = data["householdId"]
    group_id = data["groupId"]
    assert user_id
    assert group_id
    assert household_id

    if not isinstance(user_id, UUID):
        user_id = UUID(user_id)
    if not isinstance(group_id, UUID):
        group_id = UUID(group_id)
    if not isinstance(household_id, UUID):
        household_id = UUID(household_id)

    try:
        yield utils.TestUser(
            user_id=user_id,
            _group_id=group_id,
            _household_id=household_id,
            token=token,
            email=user_data["email"],
            username=user_data["username"],
            full_name=user_data["fullName"],
            password=user_data["password"],
            repos=get_repositories(session, group_id=group_id, household_id=household_id),
        )
    finally:
        # TODO: Delete User after test
        pass


@fixture(scope="module")
def g2_user(session: Session, admin_token, api_client: TestClient):
    group = random_string(12)

    # Create the user
    create_data = {
        "fullName": utils.random_string(),
        "username": utils.random_string(),
        "email": utils.random_email(),
        "password": "useruser",
        "group": group,
        "household": "Family",
        "admin": False,
        "tokens": [],
    }

    api_client.post(api_routes.admin_groups, json={"name": group}, headers=admin_token)
    response = api_client.post(api_routes.users, json=create_data, headers=admin_token)

    assert response.status_code == 201

    # Log in as this user
    form_data = {"username": create_data["email"], "password": "useruser"}

    token = utils.login(form_data, api_client)

    self_response = api_client.get(api_routes.users_self, headers=token)

    assert self_response.status_code == 200

    user_id = json.loads(self_response.text).get("id")
    group_id = json.loads(self_response.text).get("groupId")
    household_id = json.loads(self_response.text).get("householdId")

    if not isinstance(user_id, UUID):
        user_id = UUID(user_id)
    if not isinstance(group_id, UUID):
        group_id = UUID(group_id)
    if not isinstance(household_id, UUID):
        household_id = UUID(household_id)

    try:
        yield utils.TestUser(
            user_id=user_id,
            _group_id=group_id,
            _household_id=household_id,
            token=token,
            email=create_data["email"],  # type: ignore
            username=create_data.get("username"),  # type: ignore
            full_name=create_data.get("fullName"),  # type: ignore
            password=create_data.get("password"),  # type: ignore
            repos=get_repositories(session, group_id=group_id, household_id=household_id),
        )
    finally:
        # TODO: Delete User after test
        pass


def _unique_user(session: Session, api_client: TestClient):
    registration = utils.user_registration_factory()
    response = api_client.post("/api/users/register", json=registration.model_dump(by_alias=True))
    assert response.status_code == 201

    form_data = {"username": registration.username, "password": registration.password}

    token = utils.login(form_data, api_client)

    user_data = api_client.get(api_routes.users_self, headers=token).json()
    assert token is not None

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
            email=user_data.get("email"),
            username=user_data.get("username"),
            full_name=user_data.get("fullName"),
            password=registration.password,
            token=token,
            repos=get_repositories(session, group_id=group_id, household_id=household_id),
        )
    finally:
        # TODO: Delete User after test
        pass


@fixture(scope="function")
def unique_user_fn_scoped(session: Session, api_client: TestClient):
    yield from _unique_user(session, api_client)


@fixture(scope="module")
def unique_user(session: Session, api_client: TestClient):
    yield from _unique_user(session, api_client)


@fixture(scope="module")
def user_tuple(session: Session, admin_token, api_client: TestClient) -> Generator[list[utils.TestUser], None, None]:
    group_name = utils.random_string()

    # Create the user
    create_data_1 = {
        "fullName": utils.random_string(),
        "username": utils.random_string(),
        "email": utils.random_email(),
        "password": "useruser",
        "group": group_name,
        "household": "Family",
        "admin": False,
        "tokens": [],
    }

    create_data_2 = {
        "fullName": utils.random_string(),
        "username": utils.random_string(),
        "email": utils.random_email(),
        "password": "useruser",
        "group": group_name,
        "household": "Family",
        "admin": False,
        "tokens": [],
    }

    api_client.post(api_routes.admin_groups, json={"name": group_name}, headers=admin_token)

    users_out = []

    for usr in [create_data_1, create_data_2]:
        response = api_client.post(api_routes.users, json=usr, headers=admin_token)
        assert response.status_code == 201

        # Log in as this user
        form_data = {"username": usr["email"], "password": "useruser"}
        token = utils.login(form_data, api_client)
        response = api_client.get(api_routes.users_self, headers=token)
        assert response.status_code == 200
        user_data = json.loads(response.text)

        user_id = user_data.get("id")
        group_id = user_data.get("groupId")
        household_id = user_data.get("householdId")

        if not isinstance(user_id, UUID):
            user_id = UUID(user_id)
        if not isinstance(group_id, UUID):
            group_id = UUID(group_id)
        if not isinstance(household_id, UUID):
            household_id = UUID(household_id)

        users_out.append(
            utils.TestUser(
                _group_id=group_id,
                _household_id=household_id,
                user_id=user_id,
                username=user_data.get("username"),
                full_name=user_data.get("fullName"),
                email=user_data.get("email"),
                password="useruser",
                token=token,
                repos=get_repositories(session, group_id=group_id, household_id=household_id),
            )
        )

    try:
        yield users_out
    finally:
        pass


@fixture(scope="module")
def user_token(admin_token, api_client: TestClient):
    # Create the user
    create_data = {
        "fullName": utils.random_string(),
        "username": utils.random_string(),
        "email": utils.random_email(),
        "password": "useruser",
        "group": "Home",
        "admin": False,
        "tokens": [],
    }

    response = api_client.post(api_routes.users, json=create_data, headers=admin_token)

    assert response.status_code == 201

    # Log in as this user
    form_data = {"username": create_data["email"], "password": "useruser"}
    return utils.login(form_data, api_client)


@fixture(scope="module")
def ldap_user():
    # Create an LDAP user directly instead of using TestClient since we don't have
    # a LDAP service set up
    with session_context() as session:
        db = get_repositories(session, group_id=None, household_id=None)
        user = db.users.create(
            {
                "username": utils.random_string(10),
                "password": "mealie_password_not_important",
                "full_name": utils.random_string(10),
                "email": utils.random_string(10),
                "admin": False,
                "auth_method": AuthMethod.LDAP,
            }
        )
    yield user
    with session_context() as session:
        db = get_repositories(session, group_id=None, household_id=None)
        db.users.delete(user.id)
