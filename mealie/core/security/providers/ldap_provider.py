from datetime import timedelta

import ldap
from fastapi import Request
from ldap.ldapobject import LDAPObject
from sqlalchemy.orm.session import Session

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security.providers.credentials_provider import CredentialsProvider
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user.user import PrivateUser

logger = root_logger.get_logger("ldap_provider")


class LDAPProvider(CredentialsProvider):
    """Authentication provider that authenticats a user against an LDAP server using username/password combination"""

    def __init__(self, session: Session, request: Request) -> None:
        super().__init__(session, request)
        self.conn = None

    async def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user given a username and password"""
        data = await self.get_request_data()
        user = self.try_get_user(data.username)
        if not user or user.password == "LDAP" or user.auth_method == AuthMethod.LDAP:
            user = self.get_user()
            if user:
                return self.get_access_token(user, data.remember_me)

        return await super().authenticate()

    def search_user(self, conn: LDAPObject) -> list[tuple[str, dict[str, list[bytes]]]] | None:
        """
        Searches for a user by LDAP_ID_ATTRIBUTE, LDAP_MAIL_ATTRIBUTE, and the provided LDAP_USER_FILTER.
        If none or multiple users are found, return False
        """
        settings = get_app_settings()

        user_filter = ""
        if settings.LDAP_USER_FILTER:
            # fill in the template provided by the user to maintain backwards compatibility
            user_filter = settings.LDAP_USER_FILTER.format(
                id_attribute=settings.LDAP_ID_ATTRIBUTE,
                mail_attribute=settings.LDAP_MAIL_ATTRIBUTE,
                input=self.request_data.username,
            )
        # Don't assume the provided search filter has (|({id_attribute}={input})({mail_attribute}={input}))
        search_filter = "(&(|({id_attribute}={input})({mail_attribute}={input})){filter})".format(
            id_attribute=settings.LDAP_ID_ATTRIBUTE,
            mail_attribute=settings.LDAP_MAIL_ATTRIBUTE,
            input=self.request_data.username,
            filter=user_filter,
        )

        user_entry: list[tuple[str, dict[str, list[bytes]]]] | None = None
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
            return None

        # we only want the entries that have a dn
        user_entry = [(dn, attr) for dn, attr in user_entry if dn]

        if len(user_entry) > 1:
            logger.warning("[LDAP] Multiple users found with the provided user filter")
            logger.debug(f"[LDAP] The following entries were returned: {user_entry}")
            conn.unbind_s()
            return None

        return user_entry

    def get_user(self) -> PrivateUser | None:
        """Given a username and password, tries to authenticate by BINDing to an
        LDAP server

        If the BIND succeeds, it will either create a new user of that username on
        the server or return an existing one.
        Returns False on failure.
        """

        settings = get_app_settings()
        db = get_repositories(self.session)

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
            return None

        user_entry = self.search_user(conn)
        if not user_entry:
            return None
        user_dn, user_attr = user_entry[0]

        # Check the credentials of the user
        try:
            logger.debug(f"[LDAP] Attempting to bind with '{user_dn}' using the provided password")
            conn.simple_bind_s(user_dn, self.request_data.password)
        except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
            logger.error("[LDAP] Bind failed")
            conn.unbind_s()
            return None

        user = self.try_get_user(self.request_data.username)

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
                    return None
                attributes[attribute_key] = user_attr[attribute_key][0].decode("utf-8")

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
