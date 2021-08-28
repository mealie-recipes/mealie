import json
from pathlib import Path

from fastapi.testclient import TestClient
from mealie.core.config import app_dirs
from mealie.schema.user import UserOut
from pytest import fixture
from tests.app_routes import AppRoutes


@fixture(scope="session")
def admin_user():
    return UserOut(
        id=1,
        fullName="Change Me",
        username="Change Me",
        email="changeme@email.com",
        group="Home",
        admin=True,
        tokens=[],
    )


@fixture(scope="session")
def new_user():
    return UserOut(
        id=3,
        fullName="My New User",
        username="My New User",
        email="newuser@email.com",
        group="Home",
        admin=False,
        tokens=[],
    )


def test_failed_login(api_client: TestClient, api_routes: AppRoutes):
    form_data = {"username": "changeme@email.com", "password": "WRONG_PASSWORD"}
    response = api_client.post(api_routes.auth_token, form_data)

    assert response.status_code == 401


def test_superuser_login(api_client: TestClient, api_routes: AppRoutes, admin_token):
    form_data = {"username": "changeme@email.com", "password": "MyPassword"}
    response = api_client.post(api_routes.auth_token, form_data)

    assert response.status_code == 200
    new_token = json.loads(response.text).get("access_token")

    response = api_client.get(api_routes.users_self, headers=admin_token)
    assert response.status_code == 200

    return {"Authorization": f"Bearer {new_token}"}


def test_init_superuser(api_client: TestClient, api_routes: AppRoutes, admin_token, admin_user: UserOut):
    response = api_client.get(api_routes.users_id(1), headers=admin_token)
    assert response.status_code == 200

    assert json.loads(response.text) == admin_user.dict(by_alias=True)


def test_create_user(api_client: TestClient, api_routes: AppRoutes, admin_token, new_user):
    create_data = {
        "fullName": "My New User",
        "email": "newuser@email.com",
        "password": "MyStrongPassword",
        "group": "Home",
        "admin": False,
        "tokens": [],
    }

    response = api_client.post(api_routes.users, json=create_data, headers=admin_token)

    assert response.status_code == 201
    assert json.loads(response.text) == new_user.dict(by_alias=True)


def test_create_user_as_non_admin(api_client: TestClient, api_routes: AppRoutes, user_token):
    create_data = {
        "fullName": "My New User",
        "email": "newuser@email.com",
        "password": "MyStrongPassword",
        "group": "Home",
        "admin": False,
        "tokens": [],
    }

    response = api_client.post(api_routes.users, json=create_data, headers=user_token)

    assert response.status_code == 403


def test_get_all_users(api_client: TestClient, api_routes: AppRoutes, admin_token, new_user, admin_user):
    response = api_client.get(api_routes.users, headers=admin_token)

    assert response.status_code == 200
    all_users = json.loads(response.text)
    assert admin_user.dict(by_alias=True) in all_users
    assert new_user.dict(by_alias=True) in all_users


def test_update_user(api_client: TestClient, api_routes: AppRoutes, admin_token):
    update_data = {"id": 1, "fullName": "Updated Name", "email": "changeme@email.com", "group": "Home", "admin": True}
    response = api_client.put(api_routes.users_id(1), headers=admin_token, json=update_data)

    assert response.status_code == 200
    assert json.loads(response.text).get("access_token")


def test_update_other_user_as_not_admin(api_client: TestClient, api_routes: AppRoutes, user_token):
    update_data = {"id": 1, "fullName": "Updated Name", "email": "changeme@email.com", "group": "Home", "admin": True}
    response = api_client.put(api_routes.users_id(1), headers=user_token, json=update_data)

    assert response.status_code == 403


def test_update_self_as_not_admin(api_client: TestClient, api_routes: AppRoutes, user_token):
    update_data = {"fullName": "User fullname", "email": "user@email.com", "group": "Home", "admin": False}
    response = api_client.put(api_routes.users_id(4), headers=user_token, json=update_data)

    assert response.status_code == 200


def test_self_demote_admin(api_client: TestClient, api_routes: AppRoutes, admin_token):
    update_data = {"fullName": "Updated Name", "email": "changeme@email.com", "group": "Home", "admin": False}
    response = api_client.put(api_routes.users_id(1), headers=admin_token, json=update_data)

    assert response.status_code == 403


def test_self_promote_admin(api_client: TestClient, api_routes: AppRoutes, user_token):
    update_data = {"id": 3, "fullName": "Updated Name", "email": "user@email.com", "group": "Home", "admin": True}
    response = api_client.put(api_routes.users_id(2), headers=user_token, json=update_data)

    assert response.status_code == 403


def test_reset_user_password(api_client: TestClient, api_routes: AppRoutes, admin_token):
    response = api_client.put(api_routes.users_id_reset_password(3), headers=admin_token)

    assert response.status_code == 200

    form_data = {"username": "newuser@email.com", "password": "MyPassword"}
    response = api_client.post(api_routes.auth_token, form_data)

    assert response.status_code == 200


def test_delete_user(api_client: TestClient, api_routes: AppRoutes, admin_token):
    response = api_client.delete(api_routes.users_id(2), headers=admin_token)

    assert response.status_code == 200


def test_update_user_image(
    api_client: TestClient, api_routes: AppRoutes, test_image_jpg: Path, test_image_png: Path, admin_token
):
    response = api_client.post(
        api_routes.users_id_image(2), files={"profile_image": test_image_jpg.open("rb")}, headers=admin_token
    )

    assert response.status_code == 200

    response = api_client.post(
        api_routes.users_id_image(2), files={"profile_image": test_image_png.open("rb")}, headers=admin_token
    )

    assert response.status_code == 200

    directory = app_dirs.USER_DIR.joinpath("2")
    assert directory.joinpath("profile_image.png").is_file()

    # Old profile images are removed
    assert 1 == len([file for file in directory.glob("profile_image.*") if file.is_file()])
