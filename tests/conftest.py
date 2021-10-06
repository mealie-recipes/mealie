from tests.pre_test import settings  # isort:skip

import json

import requests
from fastapi.testclient import TestClient
from pytest import fixture

from mealie.app import app
from mealie.db.db_setup import SessionLocal, generate_session
from mealie.db.init_db import main
from tests.app_routes import AppRoutes
from tests.test_config import TEST_DATA
from tests.utils.factories import random_email, random_string, user_registration_factory
from tests.utils.fixture_schemas import TestUser
from tests.utils.recipe_data import get_raw_no_image, get_raw_recipe, get_recipe_test_cases

main()


def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@fixture(scope="session")
def api_client():

    app.dependency_overrides[generate_session] = override_get_db

    yield TestClient(app)

    try:
        settings.DB_PROVIDER.db_path.unlink()  # Handle SQLite Provider
    except Exception:
        pass


@fixture(scope="session")
def api_routes():
    return AppRoutes()


@fixture(scope="session")
def test_image_jpg():
    return TEST_DATA.joinpath("images", "test_image.jpg")


@fixture(scope="session")
def test_image_png():
    return TEST_DATA.joinpath("images", "test_image.png")


def login(form_data, api_client: requests, api_routes: AppRoutes):
    response = api_client.post(api_routes.auth_token, form_data)
    assert response.status_code == 200
    token = json.loads(response.text).get("access_token")
    return {"Authorization": f"Bearer {token}"}


@fixture(scope="session")
def admin_token(api_client: requests, api_routes: AppRoutes):
    form_data = {"username": "changeme@email.com", "password": settings.DEFAULT_PASSWORD}
    return login(form_data, api_client, api_routes)


@fixture(scope="session")
def g2_user(admin_token, api_client: requests, api_routes: AppRoutes):
    # Create the user
    create_data = {
        "fullName": random_string(),
        "username": random_string(),
        "email": random_email(),
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

    token = login(form_data, api_client, api_routes)

    self_response = api_client.get(api_routes.users_self, headers=token)

    assert self_response.status_code == 200

    user_id = json.loads(self_response.text).get("id")
    group_id = json.loads(self_response.text).get("groupId")

    return TestUser(user_id=user_id, group_id=group_id, token=token)


@fixture(scope="session")
def user_token(admin_token, api_client: requests, api_routes: AppRoutes):
    # Create the user
    create_data = {
        "fullName": random_string(),
        "username": random_string(),
        "email": random_email(),
        "password": "useruser",
        "group": "Home",
        "admin": False,
        "tokens": [],
    }

    response = api_client.post(api_routes.users, json=create_data, headers=admin_token)

    assert response.status_code == 201

    # Log in as this user
    form_data = {"username": create_data["email"], "password": "useruser"}
    return login(form_data, api_client, api_routes)


@fixture(scope="session")
def raw_recipe():
    return get_raw_recipe()


@fixture(scope="session")
def raw_recipe_no_image():
    return get_raw_no_image()


@fixture(scope="session")
def recipe_store():
    return get_recipe_test_cases()


@fixture(scope="module")
def unique_user(api_client: TestClient, api_routes: AppRoutes):
    registration = user_registration_factory()

    response = api_client.post("/api/users/register", json=registration.dict(by_alias=True))
    assert response.status_code == 201

    form_data = {"username": registration.username, "password": registration.password}

    token = login(form_data, api_client, api_routes)

    user_data = api_client.get(api_routes.users_self, headers=token).json()
    assert token is not None

    try:
        yield TestUser(group_id=user_data.get("groupId"), user_id=user_data.get("id"), token=token)
    finally:
        # TODO: Delete User after test
        pass


@fixture(scope="session")
def admin_user(api_client: TestClient, api_routes: AppRoutes):

    form_data = {"username": "changeme@email.com", "password": settings.DEFAULT_PASSWORD}

    token = login(form_data, api_client, api_routes)

    user_data = api_client.get(api_routes.users_self, headers=token).json()
    assert token is not None

    assert user_data.get("admin") is True
    assert user_data.get("groupId") is not None
    assert user_data.get("id") is not None

    try:
        yield TestUser(group_id=user_data.get("groupId"), user_id=user_data.get("id"), token=token)
    finally:
        # TODO: Delete User after test
        pass
