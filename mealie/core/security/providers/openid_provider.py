from datetime import timedelta
from functools import lru_cache

import requests
from authlib.jose import JsonWebKey, JsonWebToken, JWTClaims, KeySet

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security.providers.auth_provider import AuthProvider
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories

logger = root_logger.get_logger("openid_provider")


class OpenIDProvider(AuthProvider):
    """Authentication provider that authenticates a user using a token from OIDC ID token"""

    async def authenticate(self) -> tuple[str, timedelta] | None:
        """Attempt to authenticate a user given a username and password"""

        claims = self.get_claims()
        if not claims:
            return None

        settings = get_app_settings()
        repos = get_repositories(self.session)

        user = self.try_get_user(claims.get("email"))
        admin_claim = settings.OIDC_ADMIN_GROUP and settings.OIDC_ADMIN_GROUP in claims.get("groups", [])

        if not user:
            if not settings.OIDC_SIGNUP_ENABLED:
                logger.debug("[OIDC] No user found. Not creating a new user - new user creation is disabled.")
                return None

            logger.debug("[OIDC] No user found. Creating new OIDC user.")

            user = repos.users.create(
                {
                    "username": claims.get("preferred_username"),
                    "password": "OIDC",
                    "full_name": claims.get("name"),
                    "email": claims.get("email"),
                    "admin": admin_claim,
                    "auth_method": AuthMethod.OIDC,
                }
            )
            self.session.commit()
            return self.get_access_token(user)  # type: ignore

        if user:
            if user.admin != admin_claim:
                logger.debug(f"[OIDC] {'Setting' if admin_claim else 'Removing'} user as admin")
                user.admin = admin_claim
                repos.users.update(user.id, user)
            return self.get_access_token(user)

        logger.info("[OIDC] Found user but their AuthMethod does not match OIDC")
        return None

    def get_claims(self) -> JWTClaims | None:
        """Get the claims from the ID token and check if the required claims are present"""
        required_claims = {"preferred_username", "name", "email"}
        jwks = OpenIDProvider.get_jwks()
        if not jwks:
            return None
        claims = JsonWebToken(["RS256"]).decode(s=self.request.cookies.get("mealie.auth._id_token.oidc"), key=jwks)
        if not claims:
            logger.warning("[OIDC] Claims not found")
            return None
        if not required_claims.issubset(claims.keys()):
            logger.error(f"[OIDC] Required claims not present. Expected: {required_claims} Actual: {claims.keys()}")
            return None
        return claims

    @lru_cache
    @staticmethod
    def get_jwks() -> KeySet | None:
        """Get the key set from the open id configuration"""
        settings = get_app_settings()

        if not settings.OIDC_READY:
            return None
        configuration = None
        with requests.get(settings.OIDC_CONFIGURATION_URL, timeout=5) as config_response:
            config_response.raise_for_status()
            configuration = config_response.json()

        if not configuration:
            logger.warning("[OIDC] Unable to fetch configuration from the OIDC_CONFIGURATION_URL")
            return None

        jwks_uri = configuration.get("jwks_uri", None)
        if not jwks_uri:
            logger.warning("[OIDC] Unable to find the jwks_uri from the OIDC_CONFIGURATION_URL")
            return None

        with requests.get(jwks_uri, timeout=5) as response:
            response.raise_for_status()
            return JsonWebKey.import_key_set(response.json())
