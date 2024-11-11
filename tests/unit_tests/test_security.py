from pathlib import Path

import ldap
import pytest
from pytest import MonkeyPatch

from mealie.core import security
from mealie.core.config import get_app_settings
from mealie.core.dependencies import validate_file_token
from mealie.core.security.providers.credentials_provider import (
    CredentialsProvider,
    CredentialsRequest,
)
from mealie.core.security.providers.ldap_provider import LDAPProvider
from mealie.db.db_setup import session_context
from mealie.db.models.users.users import AuthMethod
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.user.auth import CredentialsRequestForm
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
        if dn == f"cn={self.user}, {self.app_settings.LDAP_BASE_DN}":
            valid_password = self.password
        elif f"cn={self.query_bind}, {self.app_settings.LDAP_BASE_DN}":
            valid_password = self.query_password

        if bind_pw == valid_password:
            return

        raise ldap.INVALID_CREDENTIALS

    # Default search mock implementation
    def search_s(self, dn, scope, filter, attrlist):
        if filter == self.app_settings.LDAP_ADMIN_FILTER:
            assert attrlist == []
            assert filter == self.app_settings.LDAP_ADMIN_FILTER
            assert dn == f"cn={self.user}, {self.app_settings.LDAP_BASE_DN}"
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
        search_filter = (
            f"(&(|({self.app_settings.LDAP_ID_ATTRIBUTE}={self.user})"
            f"({self.app_settings.LDAP_MAIL_ATTRIBUTE}={self.user})){user_filter})"
        )
        assert filter == search_filter
        assert dn == self.app_settings.LDAP_BASE_DN
        assert scope == ldap.SCOPE_SUBTREE

        return [
            (
                f"cn={self.user}, {self.app_settings.LDAP_BASE_DN}",
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


def setup_env(monkeypatch: MonkeyPatch, **kwargs):
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
    monkeypatch.setenv(
        "LDAP_USER_FILTER",
        "(&(objectClass=user)(|({id_attribute}={input})({mail_attribute}={input})))",
    )

    return user, mail, name, password, query_bind, query_password


def test_create_file_token():
    file_path = Path(__file__).parent
    file_token = security.create_file_token(file_path)

    assert file_path == validate_file_token(file_token)


def get_provider(session, username: str, password: str):
    request_data = CredentialsRequest(username=username, password=password)
    return LDAPProvider(session, request_data)


def test_ldap_user_creation(monkeypatch: MonkeyPatch):
    user, mail, name, password, query_bind, query_password = setup_env(monkeypatch)

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(user, password, False, query_bind, query_password, mail, name)

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        provider = get_provider(session, user, password)
        result = provider.get_user()

    app_settings = get_app_settings()

    assert result
    assert result.username == user
    assert result.email == mail
    assert result.full_name == name
    assert result.admin is False
    assert result.group == app_settings.DEFAULT_GROUP
    assert result.household == app_settings.DEFAULT_HOUSEHOLD
    assert result.auth_method == AuthMethod.LDAP


@pytest.mark.parametrize("valid_group", [True, False])
@pytest.mark.parametrize("valid_household", [True, False])
def test_ldap_user_creation_invalid_group_or_household(
    unfiltered_database: AllRepositories, monkeypatch: MonkeyPatch, valid_group: bool, valid_household: bool
):
    user, mail, name, password, query_bind, query_password = setup_env(monkeypatch)
    if not valid_group:
        monkeypatch.setenv("DEFAULT_GROUP", random_string())
    if not valid_household:
        monkeypatch.setenv("DEFAULT_HOUSEHOLD", random_string())

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(user, password, False, query_bind, query_password, mail, name)

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        provider = get_provider(session, user, password)
        try:
            result = provider.get_user()
        except ValueError:
            result = None

    if valid_group and valid_household:
        assert result
    else:
        assert not result

    # check if the user exists in the db
    user = unfiltered_database.users.get_by_username(user)
    if valid_group and valid_household:
        assert user
    else:
        assert not user


def test_ldap_user_creation_fail(monkeypatch: MonkeyPatch):
    user, mail, name, password, query_bind, query_password = setup_env(monkeypatch)

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(user, password, False, query_bind, query_password, mail, name)

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        provider = get_provider(session, user, password + "a")
        result = provider.get_user()

    assert result is None


def test_ldap_user_creation_non_admin(monkeypatch: MonkeyPatch):
    user, mail, name, password, query_bind, query_password = setup_env(monkeypatch)
    monkeypatch.setenv("LDAP_ADMIN_FILTER", "(memberOf=cn=admins,dc=example,dc=com)")

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(user, password, False, query_bind, query_password, mail, name)

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        provider = get_provider(session, user, password)
        result = provider.get_user()

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
        provider = get_provider(session, user, password)
        result = provider.get_user()

    assert result
    assert result.username == user
    assert result.email == mail
    assert result.full_name == name
    assert result.admin


def test_ldap_disabled(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("LDAP_AUTH_ENABLED", "False")

    get_app_settings.cache_clear()

    with session_context() as session:
        form = CredentialsRequestForm("username", "password", False)
        provider = security.get_auth_provider(session, form)

    assert isinstance(provider, CredentialsProvider)


def test_user_login_ldap_auth_method(monkeypatch: MonkeyPatch, ldap_user: PrivateUser):
    """
    Test login from a user who was originally created in Mealie, but has since been converted
    to LDAP auth method
    """
    _, _, name, ldap_password, query_bind, query_password = setup_env(monkeypatch)

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock(
            ldap_user.username,
            ldap_password,
            False,
            query_bind,
            query_password,
            ldap_user.email,
            name,
        )

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()

    with session_context() as session:
        provider = get_provider(session, ldap_user.username, ldap_password)
        result = provider.get_user()

    assert result
    assert result.username == ldap_user.username
    assert result.email == ldap_user.email
    assert result.full_name == ldap_user.full_name
    assert result.admin == ldap_user.admin
    assert result.auth_method == AuthMethod.LDAP
