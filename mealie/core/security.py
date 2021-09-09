from datetime import datetime, timedelta
from pathlib import Path

from jose import jwt
from mealie.core.config import settings
from mealie.db.database import db
from mealie.schema.user import UserInDB
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def user_from_ldap(session, username: str, password: str) -> UserInDB:
    """Given a username and password, tries to authenticate by BINDing to an
    LDAP server

    If the BIND succeeds, it will either create a new user of that username on
    the server or return an existing one.
    Returns False on failure.
    """
    import ldap

    conn = ldap.initialize(settings.LDAP_SERVER_URL)
    user_dn = settings.LDAP_BIND_TEMPLATE.format(username)
    try:
        conn.simple_bind_s(user_dn, password)
    except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
        return False

    user = db.users.get(session, username, "username", any_case=True)
    if not user:
        user = db.users.create(
            session,
            {
                "username": username,
                "password": "LDAP",
                # Fill the next two values with something unique and vaguely
                # relevant
                "full_name": username,
                "email": username,
            },
        )

    if settings.LDAP_ADMIN_FILTER:
        user.admin = len(conn.search_s(user_dn, ldap.SCOPE_BASE, settings.LDAP_ADMIN_FILTER, [])) > 0
        db.users.update(session, user.id, user)

    return user


def create_access_token(data: dict(), expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expires_delta = expires_delta or timedelta(hours=settings.TOKEN_TIME)

    expire = datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)


def create_file_token(file_path: Path) -> bool:
    token_data = {"file": str(file_path)}
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))


def authenticate_user(session, email: str, password: str) -> UserInDB:
    user: UserInDB = db.users.get(session, email, "email", any_case=True)

    if not user:
        user = db.users.get(session, email, "username", any_case=True)
    if settings.LDAP_AUTH_ENABLED and (not user or user.password == "LDAP"):
        return user_from_ldap(session, email, password)
    if not user:
        return False

    if not verify_password(password, user.password):
        return False
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain string to a hashed password

    Args:
        plain_password (str): raw password string
        hashed_password (str): hashed password from the database

    Returns:
        bool: Returns True if a match return False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Takes in a raw password and hashes it. Used prior to saving
    a new password to the database.

    Args:
        password (str): Password String

    Returns:
        str: Hashed Password
    """
    return pwd_context.hash(password)
