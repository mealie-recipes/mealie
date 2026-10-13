import base64
import json
from typing import Any

from django.http import HttpResponse
from django.middleware.gzip import GZipMiddleware
from itsdangerous import BadSignature, TimestampSigner

from mealie.core.config import get_app_settings


class SignedSessionMiddleware:
    """Preserve the signed `session` cookie used for browser OIDC state."""

    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response
        self.signer = TimestampSigner(get_app_settings().SESSION_SECRET)

    def __call__(self, request: Any) -> Any:
        initial_empty = True
        request.session = {}
        if cookie := request.COOKIES.get("session"):
            try:
                request.session = json.loads(
                    base64.b64decode(self.signer.unsign(cookie.encode(), max_age=14 * 24 * 3600))
                )
                initial_empty = False
            except BadSignature, ValueError:
                pass
        response = self.get_response(request)
        if request.session:
            payload = self.signer.sign(base64.b64encode(json.dumps(request.session).encode())).decode()
            response.set_cookie("session", payload, max_age=14 * 24 * 3600, httponly=True, samesite="lax", path="/")
        elif not initial_empty:
            response.delete_cookie("session", path="/", samesite="lax")
        return response


class CORSMiddleware:
    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        if get_app_settings().PRODUCTION or not request.headers.get("origin"):
            return self.get_response(request)
        origin = request.headers["origin"]
        preflight = request.method == "OPTIONS" and "access-control-request-method" in request.headers
        if preflight:
            response = HttpResponse(
                "OK" if origin == "http://localhost:3000" else "Disallowed CORS origin",
                status=200 if origin == "http://localhost:3000" else 400,
            )
            response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
            response.headers["Access-Control-Max-Age"] = "600"
            if headers := request.headers.get("access-control-request-headers"):
                response.headers["Access-Control-Allow-Headers"] = headers
        else:
            response = self.get_response(request)
        response.headers["Access-Control-Allow-Credentials"] = "true"
        if origin == "http://localhost:3000":
            response.headers["Access-Control-Allow-Origin"] = origin
            from django.utils.cache import patch_vary_headers

            patch_vary_headers(response, ["Origin"])
        return response


class MealieGZipMiddleware(GZipMiddleware):
    def process_response(self, request: Any, response: Any) -> Any:
        if response.get("Content-Type", "").startswith("text/event-stream"):
            return response
        if not response.streaming and len(response.content) < 1000:
            return response
        return super().process_response(request, response)
