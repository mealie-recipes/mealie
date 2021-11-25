import json

import requests
from pytest import fixture
from starlette.testclient import TestClient

from tests import utils


@fixture(scope="module")
def g2_user(admin_token, api_client: requests, api_routes: utils.AppRoutes):
    # Create the user
    create_data = {
        "fullName": utils.random_string(),
        "username": utils.random_string(),
        "email": utils.random_email(),
        "password": "useruser",
        "group": "New Group",
        "admin": False,
        "tokens": [],
    }

    response = api_client.post(api_routes.groups, json={"name": "New Group"}, headers=admin_token)
    response = api_client.post(api_routes.users, json=create_data, headers=admin_token)

    assert response.status_code == 201

    # Log in as this user
    form_data = {"username": create_data["email"], "password": "useruser"}

    token = utils.login(form_data, api_client, api_routes)

    self_response = api_client.get(api_routes.users_self, headers=token)

    assert self_response.status_code == 200

    user_id = json.loads(self_response.text).get("id")
    group_id = json.loads(self_response.text).get("groupId")

    try:
        yield utils.TestUser(user_id=user_id, group_id=group_id, token=token, email=create_data["email"])
    finally:
        # TODO: Delete User after test
        pass


@fixture(scope="module")
def unique_user(api_client: TestClient, api_routes: utils.AppRoutes):
    registration = utils.user_registration_factory()
    response = api_client.post("/api/users/register", json=registration.dict(by_alias=True))
    assert response.status_code == 201

    form_data = {"username": registration.username, "password": registration.password}

    token = utils.login(form_data, api_client, api_routes)

    user_data = api_client.get(api_routes.users_self, headers=token).json()
    assert token is not None

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


@fixture(scope="session")
def user_token(admin_token, api_client: requests, api_routes: utils.AppRoutes):
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
    return utils.login(form_data, api_client, api_routes)
