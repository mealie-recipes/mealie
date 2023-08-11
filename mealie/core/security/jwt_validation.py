import json

import requests
from jwcrypto import jwk, jwt

from mealie.core.config import get_app_settings


def _get_jwks() -> jwk.JWKSet:
    # JWKS is retrieved from the jwks endpoint
    settings = get_app_settings()
    jwk_data = requests.get(settings.JWT_AUTH_JWK_SET_URL)
    return jwk.JWKSet().from_json(jwk_data.text)


def get_claims_from_jwt_assertion(jwt_assertion: str):
    jwks = _get_jwks()
    token = jwt.JWT(jwt=jwt_assertion, key=jwks)
    return json.loads(token.claims)
