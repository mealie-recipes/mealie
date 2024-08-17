import json

import pytest
from fastapi.testclient import TestClient

from mealie.db.db_setup import session_context
from mealie.schema.user.user import PrivateUser
from mealie.services.user_services.password_reset_service import PasswordResetService
from tests.utils import api_routes
from tests.utils.factories import random_string
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
        assert cased_email

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
        assert cased_email

    with session_context() as session:
        service = PasswordResetService(session)
        token = service.generate_reset_token(cased_email)
        assert token is None
