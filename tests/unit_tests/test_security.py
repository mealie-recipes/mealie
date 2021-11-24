from pathlib import Path

from pytest import MonkeyPatch

from mealie.core import security
from mealie.core.config import get_app_settings
from mealie.core.dependencies import validate_file_token
from mealie.db.db_setup import create_session
from tests.utils.factories import random_string


def test_create_file_token():
    file_path = Path(__file__).parent
    file_token = security.create_file_token(file_path)

    assert file_path == validate_file_token(file_token)


def test_ldap_authentication_mocked(monkeypatch: MonkeyPatch):
    import ldap

    user = random_string(10)
    password = random_string(10)
    bind_template = "cn={},dc=example,dc=com"
    admin_filter = "(memberOf=cn=admins,dc=example,dc=com)"
    monkeypatch.setenv("LDAP_AUTH_ENABLED", "true")
    monkeypatch.setenv("LDAP_SERVER_URL", "")  # Not needed due to mocking
    monkeypatch.setenv("LDAP_BIND_TEMPLATE", bind_template)
    monkeypatch.setenv("LDAP_ADMIN_FILTER", admin_filter)

    class LdapConnMock:
        def simple_bind_s(self, dn, bind_pw):
            assert dn == bind_template.format(user)
            return bind_pw == password

        def search_s(self, dn, scope, filter, attrlist):
            assert attrlist == []
            assert filter == admin_filter
            assert dn == bind_template.format(user)
            assert scope == ldap.SCOPE_BASE
            return [()]

    def ldap_initialize_mock(url):
        assert url == ""
        return LdapConnMock()

    monkeypatch.setattr(ldap, "initialize", ldap_initialize_mock)

    get_app_settings.cache_clear()
    result = security.authenticate_user(create_session(), user, password)
    assert result is not False
    assert result.username == user
