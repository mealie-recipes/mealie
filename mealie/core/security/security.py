import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
from sqlalchemy.orm.session import Session

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security.hasher import get_hasher
from mealie.core.security.providers.auth_provider import AuthProvider
from mealie.core.security.providers.credentials_provider import CredentialsProvider
from mealie.core.security.providers.ldap_provider import LDAPProvider
from mealie.schema.user.auth import CredentialsRequest, CredentialsRequestForm

ALGORITHM = "HS256"

logger = root_logger.get_logger("security")


def get_auth_provider(session: Session, data: CredentialsRequestForm) -> AuthProvider:
    settings = get_app_settings()

    credentials_request = CredentialsRequest(**data.__dict__)
    if settings.LDAP_ENABLED:
        return LDAPProvider(session, credentials_request)

    return CredentialsProvider(session, credentials_request)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    settings = get_app_settings()

    to_encode = data.copy()
    expires_delta = expires_delta or timedelta(hours=settings.TOKEN_TIME)

    expire = datetime.now(UTC) + expires_delta

    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)


def create_file_token(file_path: Path) -> str:
    token_data = {"file": str(file_path)}
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))


def create_recipe_slug_token(file_path: str | Path) -> str:
    token_data = {"slug": str(file_path)}
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))


def hash_password(password: str) -> str:
    """Takes in a raw password and hashes it. Used prior to saving a new password to the database."""
    return get_hasher().hash(password)


def url_safe_token() -> str:
    """Generates a cryptographic token without embedded data. Used for password reset tokens and invitation tokens"""
    return secrets.token_urlsafe(24)
