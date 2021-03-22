import json

import requests
from pytest import fixture

BASE = "/api/users"
TOKEN_URL = "/api/auth/token"


@fixture(scope="session")
def default_user():
    return {"id": 1, "fullName": "Change Me", "email": "changeme@email.com", "group": "Home", "admin": True}


@fixture(scope="session")
def new_user():
    return {"id": 2, "fullName": "My New User", "email": "newuser@email.com", "group": "Home", "admin": False}


def test_superuser_login(api_client: requests):
    form_data = {"username": "changeme@email.com", "password": "MyPassword"}
    response = api_client.post(TOKEN_URL, form_data)

    assert response.status_code == 200
    token = json.loads(response.text).get("access_token")

    return {"Authorization": f"Bearer {token}"}


def test_init_superuser(api_client: requests, token, default_user):
    response = api_client.get(f"{BASE}/1", headers=token)
    assert response.status_code == 200

    assert json.loads(response.text) == default_user


def test_create_user(api_client: requests, token, new_user):
    create_data = {
        "fullName": "My New User",
        "email": "newuser@email.com",
        "password": "MyStrongPassword",
        "group": "Home",
        "admin": False,
    }

    response = api_client.post(f"{BASE}", json=create_data, headers=token)

    assert response.status_code == 201
    assert json.loads(response.text) == new_user
    assert True


def test_get_all_users(api_client: requests, token, new_user, default_user):
    response = api_client.get(f"{BASE}", headers=token)

    assert response.status_code == 200

    assert json.loads(response.text) == [default_user, new_user]


def test_update_user(api_client: requests, token):
    update_data = {"id": 1, "fullName": "Updated Name", "email": "updated@email.com", "group": "Home", "admin": True}
    response = api_client.put(f"{BASE}/1", headers=token, json=update_data)

    assert response.status_code == 200
    assert json.loads(response.text).get("access_token")


def test_delete_user(api_client: requests, token):
    response = api_client.delete(f"{BASE}/2", headers=token)

    assert response.status_code == 200
