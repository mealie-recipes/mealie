import ldap
from ldap.ldapobject import LDAPObject
from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.settings.settings import AppSettings
from mealie.db.models.users.users import AuthMethod

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.user.user import PrivateUser

logger = root_logger.get_logger("security.ldap")


def search_user(conn: LDAPObject, username: str):
    """
    Searches for a user by LDAP_ID_ATTRIBUTE, LDAP_MAIL_ATTRIBUTE, and the provided LDAP_USER_FILTER.
    If none or multiple users are found, return False
    """
    settings = get_app_settings()

    user_filter = ""
    if settings.LDAP_USER_FILTER:
        # fill in the template provided by the user to maintain backwards compatibility
        user_filter = settings.LDAP_USER_FILTER.format(
            id_attribute=settings.LDAP_ID_ATTRIBUTE, mail_attribute=settings.LDAP_MAIL_ATTRIBUTE, input=username
        )
    # Don't assume the provided search filter has (|({id_attribute}={input})({mail_attribute}={input}))
    search_filter = "(&(|({id_attribute}={input})({mail_attribute}={input})){filter})".format(
        id_attribute=settings.LDAP_ID_ATTRIBUTE,
        mail_attribute=settings.LDAP_MAIL_ATTRIBUTE,
        input=username,
        filter=user_filter,
    )

    user_entry = None
    try:
        logger.debug(f"[LDAP] Starting search with filter: {search_filter}")
        user_entry = conn.search_s(
            settings.LDAP_BASE_DN,
            ldap.SCOPE_SUBTREE,
            search_filter,
            [settings.LDAP_ID_ATTRIBUTE, settings.LDAP_NAME_ATTRIBUTE, settings.LDAP_MAIL_ATTRIBUTE],
        )
    except ldap.FILTER_ERROR:
        logger.error("[LDAP] Bad user search filter")

    if not user_entry:
        conn.unbind_s()
        logger.error("[LDAP] No user was found with the provided user filter")
        return False

    # we only want the entries that have a dn
    user_entry: list[tuple[str, dict]] = [(dn, attr) for dn, attr in user_entry if dn]

    if len(user_entry) > 1:
        logger.warning("[LDAP] Multiple users found with the provided user filter")
        logger.debug(f"[LDAP] The following entries were returned: {user_entry}")
        conn.unbind_s()
        return False

    return user_entry


def get_user(db: AllRepositories, username: str, password: str) -> PrivateUser | bool:
    """Given a username and password, tries to authenticate by BINDing to an
    LDAP server

    If the BIND succeeds, it will either create a new user of that username on
    the server or return an existing one.
    Returns False on failure.
    """

    settings = get_app_settings()

    if settings.LDAP_TLS_INSECURE:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    conn = ldap.initialize(settings.LDAP_SERVER_URL)
    conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    conn.set_option(ldap.OPT_REFERRALS, 0)

    if settings.LDAP_TLS_CACERTFILE:
        conn.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.LDAP_TLS_CACERTFILE)
        conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)

    if settings.LDAP_ENABLE_STARTTLS:
        conn.start_tls_s()

    try:
        conn.simple_bind_s(settings.LDAP_QUERY_BIND, settings.LDAP_QUERY_PASSWORD)
    except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
        logger.error("[LDAP] Unable to bind to with provided user/password")
        conn.unbind_s()
        return False

    user_filter = ""
    if settings.LDAP_USER_FILTER:
        # fill in the template provided by the user to maintain backwards compatibility
        user_filter = settings.LDAP_USER_FILTER.format(
            id_attribute=settings.LDAP_ID_ATTRIBUTE, mail_attribute=settings.LDAP_MAIL_ATTRIBUTE, input=username
        )
    # Don't assume the provided search filter has (|({id_attribute}={input})({mail_attribute}={input}))
    search_filter = "(&(|({id_attribute}={input})({mail_attribute}={input})){filter})".format(
        id_attribute=settings.LDAP_ID_ATTRIBUTE,
        mail_attribute=settings.LDAP_MAIL_ATTRIBUTE,
        input=username,
        filter=user_filter,
    )

    user_entry = None
    try:
        logger.debug(f"[LDAP] Starting search with filter: {search_filter}")
        user_entry = conn.search_s(
            settings.LDAP_BASE_DN,
            ldap.SCOPE_SUBTREE,
            search_filter,
            [settings.LDAP_ID_ATTRIBUTE, settings.LDAP_NAME_ATTRIBUTE, settings.LDAP_MAIL_ATTRIBUTE],
        )
    except ldap.FILTER_ERROR:
        logger.error("[LDAP] Bad user search filter")

    if not user_entry:
        conn.unbind_s()
        logger.error("[LDAP] No user was found with the provided user filter")
        return False

    # we only want the entries that have a dn
    user_entry: list[tuple[str, dict]] = [(dn, attr) for dn, attr in user_entry if dn]

    if len(user_entry) > 1:
        logger.warning("[LDAP] Multiple users found with the provided user filter")
        logger.debug(f"[LDAP] The following entries were returned: {user_entry}")
        conn.unbind_s()
        return False

    user_dn, user_attr = user_entry[0]

    # Check the credentials of the user
    try:
        logger.debug(f"[LDAP] Attempting to bind with '{user_dn}' using the provided password")
        conn.simple_bind_s(user_dn, password)
    except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
        logger.error("[LDAP] Bind failed")
        conn.unbind_s()
        return False

    # Check for existing user
    user = db.users.get_one(username, "email", any_case=True)
    if not user:
        user = db.users.get_one(username, "username", any_case=True)

    if user is None:
        logger.debug("[LDAP] User is not in Mealie. Creating a new account")

        attribute_keys = {
            settings.LDAP_ID_ATTRIBUTE: "username",
            settings.LDAP_NAME_ATTRIBUTE: "name",
            settings.LDAP_MAIL_ATTRIBUTE: "mail",
        }
        attributes = {}
        for attribute_key, attribute_name in attribute_keys.items():
            if attribute_key not in user_attr or len(user_attr[attribute_key]) == 0:
                logger.error(
                    f"[LDAP] Unable to create user due to missing '{attribute_name}' ('{attribute_key}') attribute"
                )
                logger.debug(f"[LDAP] User has the following attributes: {user_attr}")
                conn.unbind_s()
                return False
            attributes[attribute_key] = user_attr.get(attribute_key)[0].decode("utf-8")

        user = db.users.create(
            {
                "username": attributes[settings.LDAP_ID_ATTRIBUTE],
                "password": "LDAP",
                "full_name": attributes[settings.LDAP_NAME_ATTRIBUTE],
                "email": attributes[settings.LDAP_MAIL_ATTRIBUTE],
                "admin": False,
                "auth_method": AuthMethod.LDAP,
            },
        )

    if settings.LDAP_ADMIN_FILTER:
        should_be_admin = len(conn.search_s(user_dn, ldap.SCOPE_BASE, settings.LDAP_ADMIN_FILTER, [])) > 0
        if user.admin != should_be_admin:
            logger.debug(f"[LDAP] {'Setting' if should_be_admin else 'Removing'} user as admin")
            user.admin = should_be_admin
            db.users.update(user.id, user)

    conn.unbind_s()
    return user
