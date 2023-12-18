from functools import lru_cache

import requests
from authlib.jose import JsonWebKey, JsonWebToken
from fastapi import Request
from sqlalchemy.orm.session import Session

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.dependencies.common import get_credentials_exception
from mealie.db.models.users import AuthMethod
from mealie.repos.all_repositories import get_repositories

settings = get_app_settings()
logger = root_logger.get_logger("oidc")


@lru_cache
def get_jwks():
    if not settings.OIDC_READY:
        return None
    configuration = None
    with requests.get(settings.OIDC_CONFIGURATION_URL, timeout=5) as config_response:
        config_response.raise_for_status()
        configuration = config_response.json()

    if not configuration:
        logger.warning("[OIDC] Unable to fetch configuration from the OIDC_CONFIGURATION_URL")
        raise get_credentials_exception()

    jwks_uri = configuration.get("jwks_uri", None)
    if not jwks_uri:
        logger.warning("[OIDC] Unable to find the jwks_uri from the OIDC_CONFIGURATION_URL")
        raise get_credentials_exception()

    with requests.get(jwks_uri, timeout=5) as response:
        response.raise_for_status()
        return JsonWebKey.import_key_set(response.json())


def get_oidc_user(request: Request, session: Session, jwks):
    required_claims = {"preferred_username", "name", "email"}

    claims = JsonWebToken(["RS256"]).decode(s=request.cookies.get("mealie.auth._id_token.oidc"), key=jwks)
    if not claims:
        logger.warning("[OIDC] Claims not found")
        raise get_credentials_exception()
    if not required_claims.issubset(claims.keys()):
        logger.error(f"[OIDC] Required claims not present. Expected: {required_claims} Actual: {claims.keys()}")
        raise get_credentials_exception()

    repos = get_repositories(session)
    user = repos.users.get_one(claims.get("email"), "email", any_case=True)
    if not user:
        user = repos.users.get_one(claims.get("email"), "username", any_case=True)

    admin_claim = settings.OIDC_ADMIN_GROUP and settings.OIDC_ADMIN_GROUP in claims.get("groups", [])

    if not user:
        if not settings.OIDC_SIGNUP_ENABLED:
            logger.debug("[OIDC] No user found. Not creating a new user - new user creation is disabled.")
            raise get_credentials_exception()

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
        session.commit()
        return user

    if user and (user.password == "OIDC" or user.auth_method == AuthMethod.OIDC):
        if user.admin != admin_claim:
            logger.debug(f"[OIDC] {'Setting' if admin_claim else 'Removing'} user as admin")
            user.admin = admin_claim
            repos.users.update(user.id, user)
        return user

    logger.info("[OIDC] Found user but their AuthMethod does not match OIDC")
    raise get_credentials_exception()
