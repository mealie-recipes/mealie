from pathlib import Path

from mealie.core import security
from mealie.routes.deps import validate_file_token
from mealie.core.config import settings
from mealie.db.db_setup import create_session


def test_create_file_token():
    file_path = Path(__file__).parent
    file_token = security.create_file_token(file_path)

    assert file_path == validate_file_token(file_token)


def test_ldap_authentication_mocked(monkeypatch):
    import ldap

    user = "testinguser"
    password = "testingpass"
    bind_template = "cn={},dc=example,dc=com"
    admin_filter = "(memberOf=cn=admins,dc=example,dc=com)"
    monkeypatch.setattr(settings, "LDAP_AUTH_ENABLED", True)
    monkeypatch.setattr(settings, "LDAP_SERVER_URL", "")  # Not needed due to mocking
    monkeypatch.setattr(settings, "LDAP_BIND_TEMPLATE", bind_template)
    monkeypatch.setattr(settings, "LDAP_ADMIN_FILTER", admin_filter)

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
    result = security.authenticate_user(create_session(), user, password)
    assert result is not False
    assert result.username == user
