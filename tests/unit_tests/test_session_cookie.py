from datetime import timedelta

from starlette.requests import Request
from starlette.responses import Response

from mealie.routes.auth.auth import SESSION_COOKIE_NAME, session_cookie_attrs, set_session_cookie


def build_request(scheme: str = "http", headers: dict[str, str] | None = None) -> Request:
    return Request(
        {
            "type": "http",
            "scheme": scheme,
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "server": ("testserver", 80),
            "headers": [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
        }
    )


def test_plain_http_gets_an_insecure_lax_cookie():
    attrs = session_cookie_attrs(build_request())

    assert attrs["secure"] is False
    assert attrs["samesite"] == "lax"


def test_https_gets_a_secure_cookie():
    attrs = session_cookie_attrs(build_request(scheme="https"))

    assert attrs["secure"] is True


def test_forwarded_proto_is_honoured_when_the_proxy_is_not_trusted():
    """uvicorn only rewrites the scheme for proxies HOST_IP trusts; narrowing it dropped `Secure`."""
    attrs = session_cookie_attrs(build_request(headers={"x-forwarded-proto": "https"}))

    assert attrs["secure"] is True


def test_the_first_hop_of_a_forwarded_chain_decides():
    """Proxies append, so the browser's own protocol is the first entry rather than the last."""
    assert session_cookie_attrs(build_request(headers={"x-forwarded-proto": "https, http"}))["secure"] is True
    assert session_cookie_attrs(build_request(headers={"x-forwarded-proto": "http, https"}))["secure"] is False


def test_embedded_over_https_relaxes_samesite():
    attrs = session_cookie_attrs(build_request(scheme="https", headers={"x-mealie-embedded": "true"}))

    assert attrs["samesite"] == "none"


def test_embedded_behind_an_untrusted_proxy_still_relaxes_samesite():
    """The regression this guards: degrading to Lax silently breaks cross-site iframe embedding."""
    attrs = session_cookie_attrs(build_request(headers={"x-forwarded-proto": "https", "x-mealie-embedded": "true"}))

    assert attrs["samesite"] == "none"


def test_embedded_over_plain_http_stays_lax():
    """Browsers reject `SameSite=None` without `Secure`, so it must not be emitted over HTTP."""
    attrs = session_cookie_attrs(build_request(headers={"x-mealie-embedded": "true"}))

    assert attrs["samesite"] == "lax"


def test_no_attribute_starlette_cannot_emit():
    """`Partitioned` needs Python 3.14; asking for it on 3.12 made every embedded login a 500."""
    assert "partitioned" not in session_cookie_attrs(
        build_request(scheme="https", headers={"x-mealie-embedded": "true"})
    )


def test_embedded_https_cookie_is_actually_sendable():
    """The attribute dict alone can't catch a value Starlette rejects, so set the cookie for real."""
    response = Response()
    set_session_cookie(
        response,
        build_request(scheme="https", headers={"x-mealie-embedded": "true"}),
        "token",
        timedelta(hours=1),
        remember_me=True,
    )

    set_cookie = next(v.decode() for k, v in response.raw_headers if k == b"set-cookie")
    assert set_cookie.startswith(f"{SESSION_COOKIE_NAME}=token;")
    assert "SameSite=none" in set_cookie
    assert "Secure" in set_cookie
    assert "Partitioned" not in set_cookie
