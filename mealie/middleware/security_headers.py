from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Swagger/Redoc load inline scripts/styles from a CDN, which a strict CSP would break, so those
# paths are left unprotected by this middleware rather than relaxing the policy for everyone else.
_DOCS_PATHS = ("/docs", "/redoc")

_CSP = (
    "default-src 'self'; "
    "img-src 'self' data: blob: https:; "
    "style-src 'self' 'unsafe-inline'; "
    "font-src 'self' data:; "
    "script-src 'self'; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "object-src 'none'; "
    "base-uri 'self'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds defense-in-depth HTTP security headers to every response (except the API docs,
    which need a looser CSP to render their own CDN-hosted assets)."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if not request.url.path.startswith(_DOCS_PATHS):
            response.headers["Content-Security-Policy"] = _CSP

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"

        return response
