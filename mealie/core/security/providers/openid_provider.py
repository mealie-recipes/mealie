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

    def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user given a username and password"""

        settings = get_app_settings()
        claims = self.data
        if not claims:
            self._logger.error("[OIDC] No claims in the id_token")
            return None

        # Log all claims for debugging
        self._logger.debug("[OIDC] Received claims:")
        for key, value in claims.items():
            self._logger.debug("[OIDC]   %s: %s", key, value)

        if not self.required_claims.issubset(claims.keys()):
            self._logger.error(
                "[OIDC] Required claims not present. Expected: %s Actual: %s",
                self.required_claims,
                claims.keys(),
            )
            return None

        # Check for empty required claims
        for claim in self.required_claims:
            if not claims.get(claim):
                self._logger.error("[OIDC] Required claim '%s' is empty", claim)
                return None

        repos = get_repositories(self.session, group_id=None, household_id=None)

        is_admin = False
        if settings.OIDC_REQUIRES_GROUP_CLAIM:
            group_claim = claims.get(settings.OIDC_GROUPS_CLAIM, []) or []
            is_admin = settings.OIDC_ADMIN_GROUP in group_claim if settings.OIDC_ADMIN_GROUP else False
            is_valid_user = settings.OIDC_USER_GROUP in group_claim if settings.OIDC_USER_GROUP else True

            if not (is_valid_user or is_admin):
                self._logger.warning(
                    "[OIDC] Successfully authenticated, but user does not have one of the required group(s). \
                    Found: %s - Required (one of): %s",
                    group_claim,
                    [settings.OIDC_USER_GROUP, settings.OIDC_ADMIN_GROUP],
                )
                return None

        user = self.try_get_user(claims.get(settings.OIDC_USER_CLAIM))
        if not user:
            if not settings.OIDC_SIGNUP_ENABLED:
                self._logger.debug("[OIDC] No user found. Not creating a new user - new user creation is disabled.")
                return None

            self._logger.debug("[OIDC] No user found. Creating new OIDC user.")

            try:
                # some IdPs don't provide a username (looking at you Google), so if we don't have the claim,
                # we'll create the user with whatever the USER_CLAIM is (default email)
                username = claims.get(
                    "preferred_username", claims.get("username", claims.get(settings.OIDC_USER_CLAIM))
                )
                user = repos.users.create(
                    {
                        "username": username,
                        "password": "OIDC",
                        "full_name": claims.get(settings.OIDC_NAME_CLAIM),
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

    @property
    def required_claims(self):
        settings = get_app_settings()

        claims = {settings.OIDC_NAME_CLAIM, "email", settings.OIDC_USER_CLAIM}
        if settings.OIDC_REQUIRES_GROUP_CLAIM:
            claims.add(settings.OIDC_GROUPS_CLAIM)
        return claims
