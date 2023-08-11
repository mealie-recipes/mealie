from pathlib import Path

import ldap
from pytest import MonkeyPatch

from mealie.core import security
from mealie.core.config import get_app_settings
from mealie.core.dependencies import validate_file_token
from mealie.db.db_setup import session_context
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user.user import PrivateUser
from tests.utils import random_string


class LdapConnMock:
    def __init__(self, user, password, admin, query_bind, query_password, mail, name) -> None:
        self.app_settings = get_app_settings()
        self.user = user
        self.password = password
        self.query_bind = query_bind
        self.query_password = query_password
        self.admin = admin
        self.mail = mail
        self.name = name

    def simple_bind_s(self, dn, bind_pw):
        if dn == "cn={}, {}".format(self.user, self.app_settings.LDAP_BASE_DN):
            valid_password = self.password
        elif "cn={}, {}".format(self.query_bind, self.app_settings.LDAP_BASE_DN):
            valid_password = self.query_password

        if bind_pw == valid_password:
            return

        raise ldap.INVALID_CREDENTIALS

    # Default search mock implementation
    def search_s(self, dn, scope, filter, attrlist):
        if filter == self.app_settings.LDAP_ADMIN_FILTER:
            assert attrlist == []
            assert filter == self.app_settings.LDAP_ADMIN_FILTER
            assert dn == "cn={}, {}".format(self.user, self.app_settings.LDAP_BASE_DN)
            assert scope == ldap.SCOPE_BASE

            if not self.admin:
                return []

            return [(dn, {})]

        assert attrlist == [
            self.app_settings.LDAP_ID_ATTRIBUTE,
            self.app_settings.LDAP_NAME_ATTRIBUTE,
            self.app_settings.LDAP_MAIL_ATTRIBUTE,
        ]
        user_filter = self.app_settings.LDAP_USER_FILTER.format(
            id_attribute=self.app_settings.LDAP_ID_ATTRIBUTE,
            mail_attribute=self.app_settings.LDAP_MAIL_ATTRIBUTE,
            input=self.user,
        )
        search_filter = "(&(|({id_attribute}={input})({mail_attribute}={input})){filter})".format(
            id_attribute=self.app_settings.LDAP_ID_ATTRIBUTE,
            mail_attribute=self.app_settings.LDAP_MAIL_ATTRIBUTE,
            input=self.user,
            filter=user_filter,
        )
        assert filter == search_filter
        assert dn == self.app_settings.LDAP_BASE_DN
        assert scope == ldap.SCOPE_SUBTREE

        return [
            (
                "cn={}, {}".format(self.user, self.app_settings.LDAP_BASE_DN),
                {
                    self.app_settings.LDAP_ID_ATTRIBUTE: [self.user.encode()],
                    self.app_settings.LDAP_NAME_ATTRIBUTE: [self.name.encode()],
                    self.app_settings.LDAP_MAIL_ATTRIBUTE: [self.mail.encode()],
                },
            )
        ]

    def set_option(self, option, invalue):
        pass

    def unbind_s(self):
        pass

    def start_tls_s(self):
        pass


def setup_env(monkeypatch: MonkeyPatch):
    user = random_string(10)
    mail = random_string(10)
    name = random_string(10)
    password = random_string(10)
    query_bind = random_string(10)
    query_password = random_string(10)
    base_dn = "(dc=example,dc=com)"
    monkeypatch.setenv("LDAP_AUTH_ENABLED", "true")
    monkeypatch.setenv("LDAP_SERVER_URL", "")  # Not needed due to mocking
    monkeypatch.setenv("LDAP_BASE_DN", base_dn)
    monkeypatch.setenv("LDAP_QUERY_BIND", query_bind)
    monkeypatch.setenv("LDAP_QUERY_PASSWORD", query_password)
    monkeypatch.setenv("LDAP_USER_FILTER", "(&(objectClass=user)(|({id_attribute}={input})({mail_attribute}={input})))")

    return user, mail, name, password, query_bind, query_password


def test_create_file_token():
    file_path = Path(__file__).parent
    file_token = security.create_file_token(file_path)

    assert file_path == validate_file_token(file_token)


def test_ldap_user_creation(monkeypatch: MonkeyPatch):
    user, mail, name, password, query_bind, query_password = setup_env(monkeypatch)

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(user, password, False, query_bind, query_password, mail, name)

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        result = security.authenticate_user(session, user, password)

    assert result
    assert result.username == user
    assert result.email == mail
    assert result.full_name == name
    assert result.admin is False


def test_ldap_user_creation_fail(monkeypatch: MonkeyPatch):
    user, mail, name, password, query_bind, query_password = setup_env(monkeypatch)

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(user, password, False, query_bind, query_password, mail, name)

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        result = security.authenticate_user(session, user, password + "a")

    assert result is False


def test_ldap_user_creation_non_admin(monkeypatch: MonkeyPatch):
    user, mail, name, password, query_bind, query_password = setup_env(monkeypatch)
    monkeypatch.setenv("LDAP_ADMIN_FILTER", "(memberOf=cn=admins,dc=example,dc=com)")

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(user, password, False, query_bind, query_password, mail, name)

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        result = security.authenticate_user(session, user, password)

    assert result
    assert result.username == user
    assert result.email == mail
    assert result.full_name == name
    assert result.admin is False


def test_ldap_user_creation_admin(monkeypatch: MonkeyPatch):
    user, mail, name, password, query_bind, query_password = setup_env(monkeypatch)
    monkeypatch.setenv("LDAP_ADMIN_FILTER", "(memberOf=cn=admins,dc=example,dc=com)")

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(user, password, True, query_bind, query_password, mail, name)

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        result = security.authenticate_user(session, user, password)

    assert result
    assert result.username == user
    assert result.email == mail
    assert result.full_name == name
    assert result.admin


def test_ldap_disabled(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("LDAP_AUTH_ENABLED", "False")

    user = random_string(10)
    password = random_string(10)

    class LdapConnMock:
        def simple_bind_s(self, dn, bind_pw):
            assert False  # When LDAP is disabled, this method should not be called

        def search_s(self, dn, scope, filter, attrlist):
            pass

        def set_option(self, option, invalue):
            pass

        def unbind_s(self):
            pass

        def start_tls_s(self):
            pass

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock()

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        security.authenticate_user(session, user, password)


def test_user_login_ldap_auth_method(monkeypatch: MonkeyPatch, ldap_user: PrivateUser):
    """
    Test login from a user who was originally created in Mealie, but has since been converted
    to LDAP auth method
    """
    _, _, name, ldap_password, query_bind, query_password = setup_env(monkeypatch)

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(ldap_user.username, ldap_password, False, query_bind, query_password, ldap_user.email, name)

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        result = security.authenticate_user(session, ldap_user.username, ldap_password)

    assert result
    assert result.username == ldap_user.username
    assert result.email == ldap_user.email
    assert result.full_name == ldap_user.full_name
    assert result.admin == ldap_user.admin
    assert result.auth_method == AuthMethod.LDAP


# ===============================================
# JWT AUTHENTICATION


def test_jwt_auth_disabled(monkeypatch: MonkeyPatch):
    # JWT is disabled so the jwt auth flow is not executed
    monkeypatch.setenv("JWT_AUTH_ENABLED", "False")
    monkeypatch.setenv("LDAP_AUTH_ENABLED", "False")
    get_app_settings.cache_clear()

    user = random_string(10)
    password = random_string(10)

    with session_context() as session:
        user = security.authenticate_user(session, user, password)
        assert user is False


def test_jwt_auth_enabled_no_jwt_assertion(monkeypatch: MonkeyPatch):
    # JWT is enabled but since there is no jwt header the jwt auth flow is not executed
    monkeypatch.setenv("JWT_AUTH_ENABLED", "True")
    monkeypatch.setenv("LDAP_AUTH_ENABLED", "False")
    get_app_settings.cache_clear()

    user = random_string(10)
    password = random_string(10)

    with session_context() as session:
        user = security.authenticate_user(session, user, password)
        assert user is False


def test_jwt_auth_enabled_non_existing_user_no_auto_signup(monkeypatch: MonkeyPatch):
    # JWT is enabled auto sign up is disabled, as the user does not exist no user is returned
    monkeypatch.setenv("JWT_AUTH_ENABLED", "True")

    user = random_string(10)
    password = random_string(10)
    jwt_assertion = "Some JWT Assertion"

    def get_claims_from_jwt_assertion_mock(jwt_assertion):
        assert jwt_assertion == "Some JWT Assertion"
        return {"email": "user@email.com"}

    monkeypatch.setattr(
        "mealie.core.security.security.get_claims_from_jwt_assertion", get_claims_from_jwt_assertion_mock
    )

    get_app_settings.cache_clear()

    with session_context() as session:
        user = security.authenticate_user(session, user, password, jwt_assertion)
        assert user is None


def test_jwt_auth_enabled_existing_user_no_auto_signup(monkeypatch: MonkeyPatch):
    # JWT is enabled auto sign up is disabled, as the user exists it is returned
    monkeypatch.setenv("JWT_AUTH_ENABLED", "True")
    jwt_assertion = "Some JWT Assertion"
    user_email = "user@email.com"

    def get_claims_from_jwt_assertion_mock(jwt_assertion):
        assert jwt_assertion == "Some JWT Assertion"
        return {"email": user_email}

    monkeypatch.setattr(
        "mealie.core.security.security.get_claims_from_jwt_assertion", get_claims_from_jwt_assertion_mock
    )

    get_app_settings.cache_clear()

    with session_context() as session:
        db = get_repositories(session)
        user = db.users.create(
            {
                "username": "username",
                "password": "mealie_password_not_important",
                "full_name": "User full name",
                "email": user_email,
                "admin": False,
            }
        )
        user = security.authenticate_user(session, user.username, user.password, jwt_assertion)
        assert user is user


def test_jwt_auth_enabled_failed_verification(monkeypatch: MonkeyPatch):
    # JWT is enabled, the jwt validation fails so the user is not authenticated
    monkeypatch.setenv("JWT_AUTH_ENABLED", "True")

    user = random_string(10)
    password = random_string(10)
    jwt_assertion = "Some JWT Assertion"

    def get_claims_from_jwt_assertion_mock(jwt_assertion):
        assert jwt_assertion == "Some JWT Assertion"
        raise Exception("Failed to verify JWT Assertion")

    monkeypatch.setattr(
        "mealie.core.security.security.get_claims_from_jwt_assertion", get_claims_from_jwt_assertion_mock
    )

    get_app_settings.cache_clear()

    with session_context() as session:
        user = security.authenticate_user(session, user, password, jwt_assertion)
        assert user is False


def test_jwt_auth_enabled_non_existing_user_auto_signup(monkeypatch: MonkeyPatch):
    # JWT is enabled, auto sign up is enabled, user does not exist so it gets created
    monkeypatch.setenv("JWT_AUTH_ENABLED", "True")
    monkeypatch.setenv("JWT_AUTH_AUTO_SIGN_UP", "True")

    user = random_string(10)
    password = random_string(10)
    jwt_assertion = "Some JWT Assertion"

    def get_claims_from_jwt_assertion_mock(jwt_assertion):
        assert jwt_assertion == "Some JWT Assertion"
        return {
            "email": "another_user@email.com",
            "user": "someusername",
            "name": "Some User Name",
        }

    monkeypatch.setattr(
        "mealie.core.security.security.get_claims_from_jwt_assertion", get_claims_from_jwt_assertion_mock
    )

    get_app_settings.cache_clear()

    with session_context() as session:
        user = security.authenticate_user(session, user, password, jwt_assertion)
        assert user.full_name == "Some User Name"
        assert user.username == "someusername"
        assert user.email == "another_user@email.com"
