import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jose import jwt

from mealie.core.config import get_app_settings
from mealie.core.security.hasher import get_hasher
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.user import PrivateUser
from mealie.services.user_services.user_service import UserService

ALGORITHM = "HS256"


class UserLockedOut(Exception):
    ...


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
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


def user_from_ldap(db: AllRepositories, username: str, password: str) -> PrivateUser | bool:
    """Given a username and password, tries to authenticate by BINDing to an
    LDAP server

    If the BIND succeeds, it will either create a new user of that username on
    the server or return an existing one.
    Returns False on failure.
    """
    import ldap

    settings = get_app_settings()

    if settings.LDAP_TLS_INSECURE:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    ldap.set_option(ldap.OPT_REFERRALS, 0)
    ldap.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    conn = ldap.initialize(settings.LDAP_SERVER_URL)

    if settings.LDAP_TLS_CACERTFILE:
        conn.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.LDAP_TLS_CACERTFILE)
        conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
    user = db.users.get_one(username, "email", any_case=True)

    if not settings.LDAP_BIND_TEMPLATE:
        return False

    if not user:
        user_bind = settings.LDAP_BIND_TEMPLATE.format(username)
        user = db.users.get_one(username, "username", any_case=True)
    else:
        user_bind = settings.LDAP_BIND_TEMPLATE.format(user.username)

    try:
        conn.simple_bind_s(user_bind, password)
    except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
        return False

    # Search "username" against "cn" attribute for Linux, "sAMAccountName" attribute
    # for Windows and "mail" attribute for email addresses. The "mail" attribute is
    # required to obtain the user's DN for the LDAP_ADMIN_FILTER.
    user_entry = conn.search_s(
        settings.LDAP_BASE_DN,
        ldap.SCOPE_SUBTREE,
        f"(&(objectClass=user)(|(cn={username})(sAMAccountName={username})(mail={username})))",
        ["name", "mail"],
    )
    if not user_entry:
        user_dn, user_attr = user_entry[0]
    else:
        return False

    if user is None:
        user = db.users.create(
            {
                "username": username,
                "password": "LDAP",
                "full_name": user_attr["name"][0],
                "email": user_attr["mail"][0],
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
    user = db.users.get_one(email, "email", any_case=True)

    if not user:
        user = db.users.get_one(email, "username", any_case=True)
    if settings.LDAP_AUTH_ENABLED and (not user or user.password == "LDAP"):
        return user_from_ldap(db, email, password)
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
