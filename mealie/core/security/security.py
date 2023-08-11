import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jose import jwt

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security import ldap
from mealie.core.security.hasher import get_hasher
from mealie.core.security.jwt_validation import get_claims_from_jwt_assertion
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.user import PrivateUser
from mealie.services.user_services.user_service import UserService

ALGORITHM = "HS256"

logger = root_logger.get_logger("security")


class UserLockedOut(Exception):
    ...


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    settings = get_app_settings()

    to_encode = data.copy()
    expires_delta = expires_delta or timedelta(hours=settings.TOKEN_TIME)

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)


def create_file_token(file_path: Path) -> str:
    token_data = {"file": str(file_path)}
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))


def create_recipe_slug_token(file_path: str | Path) -> str:
    token_data = {"slug": str(file_path)}
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))


def _create_new_jwt_user(db: AllRepositories, claims: dict) -> PrivateUser:
    settings = get_app_settings()
    return db.users.create(
        {
            "full_name": claims[settings.JWT_AUTH_NAME_CLAIM],
            "username": claims[settings.JWT_AUTH_USERNAME_CLAIM],
            "email": claims[settings.JWT_AUTH_EMAIL_CLAIM],
            "password": hash_password(secrets.token_urlsafe(13)),  # 13 char long random password
            "group": settings.DEFAULT_GROUP,
            "admin": False,
        }
    )


def authenticate_user(session, email: str, password: str, jwt_assertion: str | None = None) -> PrivateUser | bool:
    settings = get_app_settings()

    db = get_repositories(session)

    if settings.JWT_AUTH_ENABLED and jwt_assertion is not None:
        try:
            jwt_claims = get_claims_from_jwt_assertion(jwt_assertion)
        except Exception:
            logger.error("[JWT] Unable to decode JWT assertion")
            return False
        user = db.users.get_one(jwt_claims[settings.JWT_AUTH_EMAIL_CLAIM], "email", any_case=True)
        if user is None and settings.JWT_AUTH_AUTO_SIGN_UP:
            user = _create_new_jwt_user(db, jwt_claims)
        return user

    user = db.users.get_one(email, "email", any_case=True)

    if not user:
        user = db.users.get_one(email, "username", any_case=True)
    if settings.LDAP_AUTH_ENABLED and (not user or user.password == "LDAP" or user.auth_method == AuthMethod.LDAP):
        return ldap.get_user(db, email, password)
    if not user:
        # To prevent user enumeration we perform the verify_password computation to ensure
        # server side time is relatively constant and not vulnerable to timing attacks.
        verify_password("abc123cba321", "$2b$12$JdHtJOlkPFwyxdjdygEzPOtYmdQF5/R5tHxw5Tq8pxjubyLqdIX5i")
        return False

    if user.login_attemps >= settings.SECURITY_MAX_LOGIN_ATTEMPTS or user.is_locked:
        raise UserLockedOut()

    elif not verify_password(password, user.password):
        user.login_attemps += 1
        db.users.update(user.id, user)

        if user.login_attemps >= settings.SECURITY_MAX_LOGIN_ATTEMPTS:
            user_service = UserService(db)
            user_service.lock_user(user)

        return False
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain string to a hashed password"""
    return get_hasher().verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Takes in a raw password and hashes it. Used prior to saving a new password to the database."""
    return get_hasher().hash(password)


def url_safe_token() -> str:
    """Generates a cryptographic token without embedded data. Used for password reset tokens and invitation tokens"""
    return secrets.token_urlsafe(24)
