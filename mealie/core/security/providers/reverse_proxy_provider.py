from datetime import timedelta

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security.providers.auth_provider import AuthProvider
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories


class ReverseProxyProvider(AuthProvider[str]):
    """Authentication provider that trusts a username forwarded by a reverse proxy header"""

    _logger = root_logger.get_logger("reverse_proxy_provider")

    def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user given a username sourced from a trusted proxy header"""
        settings = get_app_settings()
        username = self.data
        if not username:
            self._logger.debug("[ReverseProxy] No username provided in header")
            return None

        user = self.try_get_user(username)
        if user:
            return self.get_access_token(user)

        if not settings.REVERSE_PROXY_AUTH_SIGNUP_ENABLED:
            self._logger.debug("[ReverseProxy] No user found. Not creating a new user - signup is disabled.")
            return None

        self._logger.debug("[ReverseProxy] No user found. Creating new reverse proxy user.")
        repos = get_repositories(self.session, group_id=None, household_id=None)
        email = username if "@" in username else f"{username}@reverse-proxy.local"
        try:
            user = repos.users.create(
                {
                    "username": username,
                    "password": "REVERSE_PROXY",
                    "full_name": username,
                    "email": email,
                    "admin": False,
                    "auth_method": AuthMethod.REVERSE_PROXY,
                }
            )
            self.session.commit()
        except Exception as e:
            self._logger.error("[ReverseProxy] Exception while creating user: %s", e)
            return None

        return self.get_access_token(user)
