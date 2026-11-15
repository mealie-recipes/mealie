import json
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from mealie.core.config import get_app_settings
from mealie.db.db_setup import session_context
from mealie.db.models.users.password_reset import PasswordResetModel
from mealie.db.models.users.users import User
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user.user import PrivateUser
from mealie.services.email import EmailService
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


def _reset_payload(token: str, email: str, password: str) -> dict:
    return {"token": token, "email": email, "password": password, "passwordConfirm": password}


def _age_token(token: str, age: timedelta) -> None:
    with session_context() as session:
        entry = session.execute(select(PasswordResetModel).filter_by(token=token)).scalar_one()
        entry.created_at = datetime.now(UTC) - age
        session.commit()


def _password_hash(user: TestUser) -> str | None:
    with session_context() as session:
        return session.execute(select(User.password).where(User.id == user.user_id)).scalar_one()


def _can_login(api_client: TestClient, email: str, password: str) -> bool:
    response = api_client.post(api_routes.auth_token, data={"username": email, "password": password})
    return response.status_code == 200


def test_password_reset_expired_token_rejected(api_client: TestClient, unique_user: TestUser):
    original_hash = _password_hash(unique_user)
    with session_context() as session:
        token = PasswordResetService(session).generate_reset_token(unique_user.email)
        assert token is not None

    _age_token(token.token, timedelta(hours=get_app_settings().PASSWORD_RESET_TOKEN_TIME, minutes=1))

    new_password = random_string(15)
    response = api_client.post(
        api_routes.users_reset_password, json=_reset_payload(token.token, unique_user.email, new_password)
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token"
    assert not _can_login(api_client, unique_user.email, new_password)
    assert _password_hash(unique_user) == original_hash


def test_password_reset_new_token_invalidates_old_token(api_client: TestClient, unique_user: TestUser):
    original_hash = _password_hash(unique_user)
    with session_context() as session:
        service = PasswordResetService(session)
        first = service.generate_reset_token(unique_user.email)
        second = service.generate_reset_token(unique_user.email)
        assert first is not None
        assert second is not None

    new_password = random_string(15)
    response = api_client.post(
        api_routes.users_reset_password, json=_reset_payload(first.token, unique_user.email, new_password)
    )
    assert response.status_code == 400
    assert _password_hash(unique_user) == original_hash

    response = api_client.post(
        api_routes.users_reset_password, json=_reset_payload(second.token, unique_user.email, new_password)
    )
    assert response.status_code == 200
    assert _can_login(api_client, unique_user.email, new_password)


def test_password_reset_deletes_all_user_tokens(unique_user: TestUser, api_client: TestClient):
    with session_context() as session:
        first = PasswordResetService(session).generate_reset_token(unique_user.email)
        assert first is not None
        session.add(PasswordResetModel(user_id=first.user_id, token=random_string(32)))
        session.commit()

    response = api_client.post(
        api_routes.users_reset_password, json=_reset_payload(first.token, unique_user.email, random_string(15))
    )
    assert response.status_code == 200

    with session_context() as session:
        remaining = session.execute(select(PasswordResetModel).filter_by(user_id=first.user_id)).scalars().all()
        assert remaining == []


def test_forgot_password_same_response_for_known_and_unknown_email(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    sent: list[str] = []
    monkeypatch.setattr(EmailService, "send_forgot_password", lambda self, address, url: sent.append(address))

    known = api_client.post(api_routes.users_forgot_password, json={"email": unique_user.email})
    unknown = api_client.post(api_routes.users_forgot_password, json={"email": f"{random_string()}@example.com"})

    assert known.status_code == unknown.status_code
    assert known.text == unknown.text
    assert sent == [unique_user.email]


def test_forgot_password_email_failure_does_not_fail_request(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    def fail(self, address, url):
        raise RuntimeError("smtp down")

    monkeypatch.setattr(EmailService, "send_forgot_password", fail)

    known = api_client.post(api_routes.users_forgot_password, json={"email": unique_user.email})
    unknown = api_client.post(api_routes.users_forgot_password, json={"email": f"{random_string()}@example.com"})

    assert known.status_code == unknown.status_code
    assert known.text == unknown.text


def test_forgot_password_creates_reset_token_for_known_user(
    api_client: TestClient, unique_user: TestUser, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(EmailService, "send_forgot_password", lambda self, address, url: None)

    response = api_client.post(api_routes.users_forgot_password, json={"email": unique_user.email})
    assert response.status_code == 200

    with session_context() as session:
        repos = get_repositories(session, group_id=None, household_id=None)
        tokens = repos.tokens_pw_reset.get_all()
        assert any(str(t.user_id) == str(unique_user.user_id) for t in tokens)
