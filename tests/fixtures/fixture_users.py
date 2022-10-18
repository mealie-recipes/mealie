import json
from typing import Generator

from pytest import fixture
from starlette.testclient import TestClient

from tests import utils
from tests.utils import api_routes
from tests.utils.factories import random_string


def build_unique_user(group: str, api_client: TestClient) -> utils.TestUser:
    group = group or random_string(12)

    registration = utils.user_registration_factory()
    response = api_client.post("/api/users/register", json=registration.dict(by_alias=True))
    assert response.status_code == 201

    form_data = {"username": registration.username, "password": registration.password}

    token = utils.login(form_data, api_client)

    user_data = api_client.get(api_routes.users_self, headers=token).json()
    assert token is not None

    return utils.TestUser(
        _group_id=user_data.get("groupId"),
        user_id=user_data.get("id"),
        email=user_data.get("email"),
        username=user_data.get("username"),
        password=registration.password,
        token=token,
    )


@fixture(scope="module")
def g2_user(admin_token, api_client: TestClient):
    group = random_string(12)
    # Create the user
    create_data = {
        "fullName": utils.random_string(),
        "username": utils.random_string(),
        "email": utils.random_email(),
        "password": "useruser",
        "group": group,
        "admin": False,
        "tokens": [],
    }

    response = api_client.post(api_routes.admin_groups, json={"name": group}, headers=admin_token)
    response = api_client.post(api_routes.users, json=create_data, headers=admin_token)

    assert response.status_code == 201

    # Log in as this user
    form_data = {"username": create_data["email"], "password": "useruser"}

    token = utils.login(form_data, api_client)

    self_response = api_client.get(api_routes.users_self, headers=token)

    assert self_response.status_code == 200

    user_id = json.loads(self_response.text).get("id")
    group_id = json.loads(self_response.text).get("groupId")

    try:
        yield utils.TestUser(
            user_id=user_id,
            _group_id=group_id,
            token=token,
            email=create_data["email"],  # type: ignore
            username=create_data.get("username"),  # type: ignore
            password=create_data.get("password"),  # type: ignore
        )
    finally:
        # TODO: Delete User after test
        pass


@fixture(scope="module")
def unique_user(api_client: TestClient):
    registration = utils.user_registration_factory()
    response = api_client.post("/api/users/register", json=registration.dict(by_alias=True))
    assert response.status_code == 201

    form_data = {"username": registration.username, "password": registration.password}

    token = utils.login(form_data, api_client)

    user_data = api_client.get(api_routes.users_self, headers=token).json()
    assert token is not None

    try:
        yield utils.TestUser(
            _group_id=user_data.get("groupId"),
            user_id=user_data.get("id"),
            email=user_data.get("email"),
            username=user_data.get("username"),
            password=registration.password,
            token=token,
        )
    finally:
        # TODO: Delete User after test
        pass


@fixture(scope="module")
def user_tuple(admin_token, api_client: TestClient) -> Generator[list[utils.TestUser], None, None]:
    group_name = utils.random_string()
    # Create the user
    create_data_1 = {
        "fullName": utils.random_string(),
        "username": utils.random_string(),
        "email": utils.random_email(),
        "password": "useruser",
        "group": group_name,
        "admin": False,
        "tokens": [],
    }

    create_data_2 = {
        "fullName": utils.random_string(),
        "username": utils.random_string(),
        "email": utils.random_email(),
        "password": "useruser",
        "group": group_name,
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

        users_out.append(
            utils.TestUser(
                _group_id=user_data.get("groupId"),
                user_id=user_data.get("id"),
                username=user_data.get("username"),
                email=user_data.get("email"),
                password="useruser",
                token=token,
            )
        )

    try:
        yield users_out
    finally:
        pass


@fixture(scope="session")
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
