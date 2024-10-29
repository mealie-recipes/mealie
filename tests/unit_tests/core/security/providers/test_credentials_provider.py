from mealie.core.security.providers.credentials_provider import CredentialsProvider
from mealie.db.models.users.users import AuthMethod
from mealie.schema.user.auth import CredentialsRequest
from tests.utils.fixture_schemas import TestUser


def test_login(unique_user: TestUser):
    data = {"username": unique_user.username, "password": unique_user.password}
    auth_provider = CredentialsProvider(unique_user.repos.session, CredentialsRequest(**data))

    assert auth_provider.authenticate() is not None


def test_login_incorrect_auth_method(unique_user: TestUser):
    db = unique_user.repos
    user = db.users.get_by_username(unique_user.username)
    user.auth_method = AuthMethod.OIDC
    db.users.update(unique_user.user_id, user)

    data = {"username": unique_user.username, "password": unique_user.password}
    auth_provider = CredentialsProvider(db.session, CredentialsRequest(**data))

    assert auth_provider.authenticate() is None
