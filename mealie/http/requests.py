from types import SimpleNamespace
from typing import Any

import httpx
from rest_framework.request import Request as DRFRequest


class Request:
    """Controller request context backed by DRF's parsed Django request."""

    def __init__(self, request: DRFRequest) -> None:
        self.drf = request
        self.headers = request.headers
        self.cookies = request.COOKIES
        self.query_params = request.query_params
        self.session = getattr(request._request, "session", {})
        self.url = httpx.URL(request.build_absolute_uri())
        self.base_url = str(httpx.URL(request.build_absolute_uri("/")))
        self.method = request.method
        self.client = SimpleNamespace(host=request.META.get("REMOTE_ADDR", "unknown"))

    async def body(self) -> bytes:
        return self.drf.body

    async def form(self) -> Any:
        return self.drf.data

    async def json(self) -> Any:
        return self.drf.data


class OAuth2PasswordBearer:
    def __init__(self, tokenUrl: str, auto_error: bool = True) -> None:
        self.token_url = tokenUrl
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> str | None:
        from mealie.http.api import HTTPException

        scheme, _, token = request.headers.get("authorization", "").partition(" ")
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(401, "Not authenticated", {"WWW-Authenticate": "Bearer"})
            return None
        return token
