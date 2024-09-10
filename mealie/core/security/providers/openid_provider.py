from datetime import timedelta

from authlib.oidc.core import UserInfo
from sqlalchemy.orm.session import Session

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security.providers.auth_provider import AuthProvider
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories


class OpenIDProvider(AuthProvider[UserInfo]):
    """Authentication provider that authenticates a user using a token from OIDC ID token"""

    _logger = root_logger.get_logger("openid_provider")

    def __init__(self, session: Session, data: UserInfo) -> None:
        super().__init__(session, data)

    async def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user given a username and password"""

        settings = get_app_settings()
        claims = self.data
        if not claims:
            self._logger.error("[OIDC] No claims in the id_token")
            return None

        repos = get_repositories(self.session, group_id=None, household_id=None)

        user = self.try_get_user(claims.get(settings.OIDC_USER_CLAIM))
        is_admin = False
        if settings.OIDC_USER_GROUP or settings.OIDC_ADMIN_GROUP:
            group_claim = claims.get(settings.OIDC_GROUPS_CLAIM, []) or []
            is_admin = settings.OIDC_ADMIN_GROUP in group_claim if settings.OIDC_ADMIN_GROUP else False
            is_valid_user = settings.OIDC_USER_GROUP in group_claim if settings.OIDC_USER_GROUP else True

            if not is_valid_user:
                self._logger.warning(
                    "[OIDC] Successfully authenticated, but user does not have the required group. \
                    Found: %s - Required: %s",
                    group_claim,
                    settings.OIDC_USER_GROUP,
                )
                return None

        if not user:
            if not settings.OIDC_SIGNUP_ENABLED:
                self._logger.debug("[OIDC] No user found. Not creating a new user - new user creation is disabled.")
                return None

            self._logger.debug("[OIDC] No user found. Creating new OIDC user.")

            try:
                user = repos.users.create(
                    {
                        "username": claims.get("preferred_username"),
                        "password": "OIDC",
                        "full_name": claims.get("name"),
                        "email": claims.get("email"),
                        "admin": is_admin,
                        "auth_method": AuthMethod.OIDC,
                    }
                )
                self.session.commit()

            except Exception as e:
                self._logger.error("[OIDC] Exception while creating user: %s", e)
                return None

            return self.get_access_token(user, settings.OIDC_REMEMBER_ME)  # type: ignore

        if user:
            if settings.OIDC_ADMIN_GROUP and user.admin != is_admin:
                self._logger.debug("[OIDC] %s user as admin", "Setting" if is_admin else "Removing")
                user.admin = is_admin
                repos.users.update(user.id, user)
            return self.get_access_token(user, settings.OIDC_REMEMBER_ME)

        self._logger.warning("[OIDC] Found user but their AuthMethod does not match OIDC")
        return None
