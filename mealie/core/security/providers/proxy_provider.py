from datetime import timedelta

from sqlalchemy.orm.session import Session
from starlette.datastructures import Headers

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security.providers.credentials_provider import CredentialsProvider
from mealie.schema.user.auth import CredentialsRequest


class ProxyProvider(CredentialsProvider):
    """Authentication provider that authenticates a user using the header(s) forwarded from a trusted proxy"""

    _logger = root_logger.get_logger("proxy_provider")

    def __init__(self, session: Session, data: CredentialsRequest) -> None:
        # Extra attributes necessary for forward auth that are not included in AuthProvider protocol nor passed
        # to get_auth_provider. Instead, we assign these later in the /auth/token route where we have access to
        # the Request object.
        self.headers: Headers
        super().__init__(session, data)

    def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user with the username supplied in the
        `REMOTE-USER` header (or the header specified by settings.REMOTE_USER_HEADER)."""
        # When proxy auth is enabled, we need to still also support authentication with the Mealie backend.
        # First we look to see if the required user header is set. If the required header is not set,
        # we fallback to authenticating using the credentials provided in the login form. If the required
        # header IS set, we attempt to match the value of this header with an existing mealie user.
        # If we fail to find an existing user, we fallback to authenticating with the Mealie backend.

        settings = get_app_settings()
        remote_user = self.headers.get(settings.REMOTE_USER_HEADER, None)

        if not remote_user:
            self._logger.debug(
                f"Required header {settings.REMOTE_USER_HEADER} not found. Falling back to internal auth."
            )
            return super().authenticate()

        user = self.try_get_user(remote_user)

        if not user:
            # For now, there is no option to automatically provision new users, i.e.
            # users who have not been previously registered as internal users. Though
            # this could be added fairly trivially.
            self._logger.debug(f"Failed to find existing user for remote user: {remote_user}")
            return super().authenticate()

        return self.get_access_token(user, False)
