from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from pathlib import Path

from jose import jwt
from passlib.context import CryptContext

from mealie.core.config import get_app_settings
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.user import PrivateUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    settings = get_app_settings()

    to_encode = data.copy()
    expires_delta = expires_delta or timedelta(hours=settings.TOKEN_TIME)

    expire = datetime.utcnow() + expires_delta

    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)


def create_file_token(file_path: Path) -> str:
    token_data = {"file": str(file_path)}
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))


def create_recipe_slug_token(file_path: str) -> str:
    token_data = {"slug": str(file_path)}
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))


def user_from_ldap(db: AllRepositories, session, username: str, password: str) -> PrivateUser:
    """Given a username and password, tries to authenticate by BINDing to an
    LDAP server

    If the BIND succeeds, it will either create a new user of that username on
    the server or return an existing one.
    Returns False on failure.
    """
    import ldap

    settings = get_app_settings()

    conn = ldap.initialize(settings.LDAP_SERVER_URL)
    user_dn = settings.LDAP_BIND_TEMPLATE.format(username)
    try:
        conn.simple_bind_s(user_dn, password)
    except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
        return False

    user = db.users.get_one(username, "username", any_case=True)
    if not user:
        user = db.users.create(
            {
                "username": username,
                "password": "LDAP",
                # Fill the next two values with something unique and vaguely
                # relevant
                "full_name": username,
                "email": username,
                "admin": False,
            },
        )

    if settings.LDAP_ADMIN_FILTER:
        user.admin = len(conn.search_s(user_dn, ldap.SCOPE_BASE, settings.LDAP_ADMIN_FILTER, [])) > 0
        db.users.update(user.id, user)

    return user


def authenticate_user(session, email: str, password: str) -> PrivateUser | bool:
    settings = get_app_settings()

    db = get_repositories(session)
    user: PrivateUser = db.users.get(email, "email", any_case=True)

    if not user:
        user = db.users.get(email, "username", any_case=True)

    if settings.LDAP_AUTH_ENABLED and (not user or user.password == "LDAP"):
        return user_from_ldap(db, session, email, password)

    if not user or not verify_password(password, user.password):
        return False

    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain string to a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Takes in a raw password and hashes it. Used prior to saving a new password to the database."""
    return pwd_context.hash(password)


def url_safe_token() -> str:
    """Generates a cryptographic token without embedded data. Used for password reset tokens and invitation tokens"""
    return secrets.token_urlsafe(24)
