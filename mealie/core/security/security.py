import secrets
from datetime import timedelta
from pathlib import Path

from sqlalchemy.orm.session import Session

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security.hasher import get_hasher
from mealie.core.security.providers.auth_provider import AuthProvider
from mealie.core.security.providers.credentials_provider import CredentialsProvider
from mealie.core.security.providers.ldap_provider import LDAPProvider
from mealie.core.security.tokens import ALGORITHM, ISS, create_access_token
from mealie.schema.user.auth import CredentialsRequest, CredentialsRequestForm

__all__ = [
    "ALGORITHM",
    "ISS",
    "create_access_token",
    "create_file_token",
    "get_auth_provider",
    "hash_password",
    "url_safe_token",
]

logger = root_logger.get_logger("security")


def get_auth_provider(session: Session, data: CredentialsRequestForm) -> AuthProvider:
    settings = get_app_settings()

    credentials_request = CredentialsRequest(**data.__dict__)
    if settings.LDAP_ENABLED:
        return LDAPProvider(session, credentials_request)

    return CredentialsProvider(session, credentials_request)


def create_file_token(file_path: Path) -> str:
    token, _ = create_access_token({"file": str(file_path)}, timedelta(minutes=30))
    return token


def hash_password(password: str) -> str:
    """Takes in a raw password and hashes it. Used prior to saving a new password to the database."""
    return get_hasher().hash(password)


def url_safe_token() -> str:
    """Generates a cryptographic token without embedded data. Used for password reset tokens and invitation tokens"""
    return secrets.token_urlsafe(24)
