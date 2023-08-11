import requests
from pytest import MonkeyPatch
import jwcrypto

from mealie.core.config import get_app_settings
from mealie.core.security.jwt_validation import get_claims_from_jwt_assertion


class MockResponse:
    @staticmethod
    def text():
        return '{"keys": [{"kid": "some_kid", "kty": "RSA", "alg": "RS256"}]}'


class MockJWT:
    def __init__(self):
        self.claims = '{"sub": "some_user_id"}'


class MockJWKSet:
    pass


def test_get_claims_from_jwt_assertion(monkeypatch: MonkeyPatch):
    def mock_get(*args, **kwargs):
        assert args[0] == "https://your-auth-provider.example.com/.well-known/jwks.json"
        return MockResponse()

    def mock_from_json(*args, **kwargs):
        return MockJWKSet()

    def mock_decode_jwt(*args, **kwargs):
        assert kwargs["jwt"] == "some_jwt_assertion"
        return MockJWT()

    # Patch requests
    monkeypatch.setattr(requests, "get", mock_get)

    # Patch jwcrypto
    monkeypatch.setattr(jwcrypto.jwk.JWKSet, "from_json", mock_from_json)
    monkeypatch.setattr(jwcrypto.jwt, "JWT", mock_decode_jwt)

    claims = get_claims_from_jwt_assertion("some_jwt_assertion")
    assert claims == {"sub": "some_user_id"}
