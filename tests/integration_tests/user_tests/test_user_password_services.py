import json

import pytest
from fastapi.testclient import TestClient

from mealie.core.config import get_app_settings
from mealie.db.db_setup import session_context
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.user.user import ChangePassword, PrivateUser
from mealie.services.user_services.password_reset_service import PasswordResetService
from tests.utils import api_routes
from tests.utils.factories import random_email, random_string
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("casing", ["lower", "upper", "mixed"])
def test_password_reset(api_client: TestClient, unique_user: TestUser, casing: str):
    cased_email = ""
    if casing == "lower":
        cased_email = unique_user.email.lower()
    elif casing == "upper":
        cased_email = unique_user.email.upper()
    else:
        for i, letter in enumerate(unique_user.email):
            if i % 2 == 0:
                cased_email += letter.upper()
            else:
                cased_email += letter.lower()
        cased_email

    with session_context() as session:
        service = PasswordResetService(session)
        token = service.generate_reset_token(cased_email)
        assert token is not None

    new_password = random_string(15)

    payload = {
        "token": token.token,
        "email": cased_email,
        "password": new_password,
        "passwordConfirm": new_password,
    }

    # Test successful password reset
    response = api_client.post(api_routes.users_reset_password, json=payload)
    assert response.status_code == 200

    # Test Login
    form_data = {"username": unique_user.email, "password": new_password}
    response = api_client.post(api_routes.auth_token, data=form_data)
    assert response.status_code == 200

    # Test Token
    new_token = json.loads(response.text).get("access_token")
    response = api_client.get(api_routes.users_self, headers={"Authorization": f"Bearer {new_token}"})
    assert response.status_code == 200

    # Test successful password reset
    response = api_client.post(api_routes.users_reset_password, json=payload)
    assert response.status_code == 400


@pytest.mark.parametrize("use_default_user", [True, False], ids=["default user", "non-default user"])
def test_update_password_without_current_password(
    api_client: TestClient, use_default_user: bool, database: AllRepositories
):
    settings = get_app_settings()
    if use_default_user:
        users = database.users.page_all(PaginationQuery(query_filter=f"email={settings._DEFAULT_EMAIL}"))
        if not users.items:
            user = database.users.create(
                {
                    "full_name": "Change Me",
                    "username": "admin",
                    "email": settings._DEFAULT_EMAIL,
                    "password": settings._DEFAULT_PASSWORD,
                    "group": settings.DEFAULT_GROUP,
                    "admin": True,
                }
            )
        else:
            user = users.items[0]
    else:
        user = database.users.create(
            {
                "full_name": "Non Default User",
                "username": "non-default-user",
                "email": random_email(),
                "password": settings._DEFAULT_PASSWORD,
                "group": settings.DEFAULT_GROUP,
                "admin": True,
            }
        )

    old_form_data = {"username": user.email, "password": settings._DEFAULT_PASSWORD}
    response = api_client.post(api_routes.auth_token, data=old_form_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    old_headers = {"Authorization": f"Bearer {token}"}

    new_password = random_string()
    payload = ChangePassword(new_password=new_password).model_dump()  # current password is not passed here
    response = api_client.put(api_routes.users_password, json=payload, headers=old_headers)
    if use_default_user:
        assert response.status_code == 200
    else:
        # even if the default password is correct, we shouldn't authenticate without passing it
        assert response.status_code == 400

    # Test Login
    new_form_data = {"username": user.email, "password": new_password}
    response = api_client.post(api_routes.auth_token, data=new_form_data)
    if use_default_user:
        assert response.status_code == 200
    else:
        assert response.status_code == 401


@pytest.mark.parametrize("casing", ["lower", "upper", "mixed"])
def test_password_reset_ldap(ldap_user: PrivateUser, casing: str):
    cased_email = ""
    if casing == "lower":
        cased_email = ldap_user.email.lower()
    elif casing == "upper":
        cased_email = ldap_user.email.upper()
    else:
        for i, letter in enumerate(ldap_user.email):
            if i % 2 == 0:
                cased_email += letter.upper()
            else:
                cased_email += letter.lower()
        cased_email

    with session_context() as session:
        service = PasswordResetService(session)
        token = service.generate_reset_token(cased_email)
        assert token is None
