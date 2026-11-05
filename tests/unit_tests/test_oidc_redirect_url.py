import pytest
from starlette.requests import Request

from mealie.routes.auth import auth


def make_request(scheme: str = "https", host: str = "mealie.example.com") -> Request:
    return Request(
        {
            "type": "http",
            "scheme": scheme,
            "server": (host, 443 if scheme == "https" else 80),
            "path": "/api/auth/oauth",
            "headers": [(b"host", host.encode())],
            "query_string": b"",
        }
    )


@pytest.mark.parametrize(
    ("base_url", "scheme", "expected"),
    [
        ("https://mealie.example.com", "http", "https://mealie.example.com/login"),
        # a BASE_URL without a scheme must not become a relative redirect URI (#6417)
        ("mealie.example.com", "https", "https://mealie.example.com/login"),
        ("mealie.example.com", "http", "http://mealie.example.com/login"),
        ("mealie.example.com/sub", "https", "https://mealie.example.com/sub/login"),
        # the default BASE_URL is ignored in favour of the request
        ("http://localhost:8080", "https", "https://mealie.example.com/login"),
    ],
)
def test_oidc_login_redirect_url(monkeypatch: pytest.MonkeyPatch, base_url: str, scheme: str, expected: str):
    monkeypatch.setattr(auth.settings, "PRODUCTION", True)
    monkeypatch.setattr(auth.settings, "BASE_URL", base_url)

    assert auth.oidc_login_redirect_url(make_request(scheme)) == expected
