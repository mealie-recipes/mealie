"""MCP transport mounted in Mealie's existing ASGI process."""

import json
import threading
import time
from urllib.parse import parse_qs, urlsplit

from fastapi import FastAPI
from mcp.server.auth.routes import build_metadata, cors_middleware
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions, RevocationOptions
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import AnyHttpUrl
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.types import Message, Receive, Scope, Send

from mealie.db.db_setup import session_context
from mealie.mcp.oauth import (
    SCOPES,
    MealieOAuthProvider,
    canonical_resource,
    issuer_url,
    mcp_enabled,
    mcp_url,
    public_base_url,
)

provider = MealieOAuthProvider()


def _startup_base_url() -> str:
    """Keep ordinary Mealie available while an invalid MCP base URL is disabled."""
    try:
        configured = public_base_url()
        parts = urlsplit(configured)
        if parts.scheme == "https" or parts.hostname in {"localhost", "127.0.0.1", "::1"}:
            return configured
    except ValueError:
        pass
    return "http://localhost:8080"


_base_url = _startup_base_url()
auth_settings = AuthSettings(
    issuer_url=AnyHttpUrl(_base_url + "/oauth"),
    resource_server_url=AnyHttpUrl(_base_url + "/mcp"),
    validate_token_resource=True,
    required_scopes=[],
    client_registration_options=ClientRegistrationOptions(
        enabled=True,
        # Unknown scopes are dropped in register_client instead of failing registration
        valid_scopes=None,
        default_scopes=list(SCOPES),
    ),
    revocation_options=RevocationOptions(enabled=True),
)
mcp = MCPServer("Mealie", auth=auth_settings, auth_server_provider=provider)
_rate_lock = threading.Lock()
_rate_buckets: dict[tuple[str, str], tuple[float, int]] = {}
_rate_limits = {
    "/mcp": (120, 60),
    "/oauth/register": (20, 3600),
    "/oauth/authorize": (60, 60),
    "/oauth/token": (60, 60),
}


def _rate_allowed(path: str, scope: Scope) -> bool:
    limit, period = _rate_limits[path]
    peer = (scope.get("client") or ("unknown", 0))[0]
    key = (path, peer)
    now = time.monotonic()
    with _rate_lock:
        if len(_rate_buckets) > 10000:
            for old_key, (start, _) in list(_rate_buckets.items()):
                if now - start > _rate_limits[old_key[0]][1]:
                    del _rate_buckets[old_key]
            while len(_rate_buckets) > 10000:
                _rate_buckets.pop(next(iter(_rate_buckets)))
        start, count = _rate_buckets.get(key, (now, 0))
        if now - start >= period:
            start, count = now, 0
        _rate_buckets[key] = (start, count + 1)
        return count < limit


async def _buffer_request(receive: Receive, max_bytes: int = 4 * 1024 * 1024) -> tuple[bytes, Receive] | None:
    body = bytearray()
    while True:
        message = await receive()
        body.extend(message.get("body", b""))
        if len(body) > max_bytes:
            return None
        if not message.get("more_body", False):
            break
    delivered = False

    async def replay():
        nonlocal delivered
        if not delivered:
            delivered = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}
        return await receive()

    return bytes(body), replay


def _challenge(
    status: int, scope: str | None = None, request_id: str | int | None = None, required: str | None = None
) -> Response:
    fields = [f'resource_metadata="{_metadata_url("oauth-protected-resource", "/mcp")}"']
    if scope:
        fields.append(f'scope="{scope}"')
    if status == 403:
        fields.append('error="insufficient_scope"')
        fields.append(f'error_description="The requested tool requires the {required or scope} scope"')
    else:
        fields.append('error="invalid_token"')
        fields.append('error_description="A valid MCP OAuth access token is required"')
    challenge = "Bearer " + ", ".join(fields)
    body: dict = {"error": "insufficient_scope" if status == 403 else "invalid_token"}
    if status == 403 and request_id is not None:
        body = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": f"MCP permission required: {scope}"}],
                "_meta": {"mcp/www_authenticate": [challenge]},
                "isError": True,
            },
        }
    return JSONResponse(
        body,
        status_code=status,
        headers={"WWW-Authenticate": challenge, "Cache-Control": "no-store"},
    )


def _metadata_path(kind: str, suffix: str) -> str:
    return f"/.well-known/{kind}{urlsplit(_base_url).path.rstrip('/')}{suffix}"


def _metadata_url(kind: str, suffix: str) -> str:
    parts = urlsplit(_base_url)
    return f"{parts.scheme}://{parts.netloc}{_metadata_path(kind, suffix)}"


class McpRouteAdapter:
    """Keep the SDK's auth middleware while exposing its routes at Mealie paths."""

    def __init__(self, sdk_app, sdk_path: str, public_path: str):
        self.sdk_app = sdk_app
        self.sdk_path = sdk_path
        self.public_path = public_path

    async def _send_tool_list(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Add tool OAuth metadata that the pinned MCP SDK cannot serialize."""
        messages: list[Message] = []

        async def capture(message: Message) -> None:
            messages.append(message)

        await self.sdk_app(scope, receive, capture)
        starts = [message for message in messages if message["type"] == "http.response.start"]
        bodies = [message for message in messages if message["type"] == "http.response.body"]
        if len(starts) != 1 or not bodies or starts[0]["status"] != 200:
            for message in messages:
                await send(message)
            return
        try:
            payload = json.loads(b"".join(message.get("body", b"") for message in bodies))
            listed = payload["result"]["tools"]
            from mealie.mcp.tools import TOOL_SCOPES

            for tool in listed:
                required_scope = TOOL_SCOPES.get(tool["name"])
                if required_scope:
                    tool["securitySchemes"] = [{"type": "oauth2", "scopes": [required_scope]}]
            content = json.dumps(payload, separators=(",", ":")).encode()
        except KeyError, TypeError, ValueError:
            for message in messages:
                await send(message)
            return
        start = dict(starts[0])
        start["headers"] = [
            (key, value) for key, value in start.get("headers", []) if key.lower() != b"content-length"
        ] + [(b"content-length", str(len(content)).encode())]
        await send(start)
        await send({"type": "http.response.body", "body": content, "more_body": False})

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        with session_context() as session:
            if not mcp_enabled(session):
                return await Response(status_code=404)(scope, receive, send)
        if self.public_path in _rate_limits and not _rate_allowed(self.public_path, scope):
            return await JSONResponse({"error": "rate_limited"}, status_code=429, headers={"Retry-After": "60"})(
                scope, receive, send
            )

        if self.public_path in {"/oauth/token", "/oauth/revoke"} and scope.get("method") == "POST":
            buffered = await _buffer_request(receive, 64 * 1024)
            if buffered is None:
                return await Response(status_code=413)(scope, receive, send)
            body, receive = buffered
            try:
                fields = parse_qs(body.decode("utf-8"), keep_blank_values=True)
            except UnicodeDecodeError:
                fields = {}
            resources = fields.get("resource", [])
            if self.public_path == "/oauth/token" and any(canonical_resource(item) is None for item in resources):
                return await JSONResponse(
                    {"error": "invalid_target", "error_description": "The resource must be this Mealie MCP URL"},
                    status_code=400,
                    headers={"Cache-Control": "no-store"},
                )(scope, receive, send)
            if self.public_path == "/oauth/revoke" and "client_secret" not in fields:
                # The SDK's revocation form model currently requires this nullable field.
                # Public OAuth clients are allowed to omit it entirely.
                original_receive = receive

                async def receive_with_empty_secret():
                    message = await original_receive()
                    if message.get("type") == "http.request":
                        return {**message, "body": body + b"&client_secret="}
                    return message

                receive = receive_with_empty_secret

        if self.public_path == "/mcp":
            header_map = {key.lower(): value for key, value in scope.get("headers", [])}
            bearer = header_map.get(b"authorization", b"").decode()
            if not bearer.lower().startswith("bearer "):
                return await _challenge(401, " ".join(SCOPES))(scope, receive, send)
            token = await provider.load_access_token(bearer[7:])
            if token is None:
                return await _challenge(401, " ".join(SCOPES))(scope, receive, send)
            if scope.get("method") == "POST":
                buffered = await _buffer_request(receive)
                if buffered is None:
                    return await Response(status_code=413)(scope, receive, send)
                body, receive = buffered
                tool_listing = False
                try:
                    request_json = json.loads(body)
                    tool_listing = request_json.get("method") == "tools/list"
                    if request_json.get("method") == "tools/call":
                        from mealie.mcp.tools import TOOL_SCOPES

                        required = TOOL_SCOPES.get(request_json.get("params", {}).get("name"))
                        if required and required not in token.scopes:
                            request_id = request_json.get("id")
                            if isinstance(request_id, bool) or not isinstance(request_id, str | int):
                                request_id = None
                            # Ask for everything the token already has plus the new scope, so
                            # clients that re-authorize with exactly this list don't lose access
                            wanted = " ".join([*token.scopes, required])
                            return await _challenge(403, wanted, request_id, required)(scope, receive, send)
                except ValueError, AttributeError, TypeError:
                    pass

                if tool_listing:
                    mapped_scope = dict(scope)
                    mapped_scope["path"] = self.sdk_path
                    mapped_scope["raw_path"] = self.sdk_path.encode()
                    return await self._send_tool_list(mapped_scope, receive, send)

        mapped_scope = dict(scope)
        mapped_scope["path"] = self.sdk_path
        mapped_scope["raw_path"] = self.sdk_path.encode()
        await self.sdk_app(mapped_scope, receive, send)


async def authorization_metadata(request: Request) -> JSONResponse:
    with session_context() as session:
        if not mcp_enabled(session):
            return JSONResponse({"detail": "Not found"}, status_code=404)
    metadata = build_metadata(
        AnyHttpUrl(issuer_url()),
        None,
        auth_settings.client_registration_options,
        auth_settings.revocation_options,
    ).model_dump(mode="json", exclude_none=True)
    metadata["client_id_metadata_document_supported"] = True
    metadata["authorization_response_iss_parameter_supported"] = True
    metadata["token_endpoint_auth_methods_supported"] = ["none", "client_secret_post", "client_secret_basic"]
    metadata["revocation_endpoint_auth_methods_supported"] = ["none", "client_secret_post", "client_secret_basic"]
    return JSONResponse(metadata, headers={"Cache-Control": "no-store"})


async def protected_resource_metadata(request: Request) -> JSONResponse:
    with session_context() as session:
        if not mcp_enabled(session):
            return JSONResponse({"detail": "Not found"}, status_code=404)
    return JSONResponse(
        {
            "resource": mcp_url(),
            "authorization_servers": [issuer_url()],
            "scopes_supported": list(SCOPES),
            "bearer_methods_supported": ["header"],
        },
        headers={"Cache-Control": "no-store"},
    )


async def _well_known_not_found(request: Request) -> JSONResponse:
    return JSONResponse({"detail": "Not found"}, status_code=404)


def register_mcp_routes(app: FastAPI) -> None:
    from mealie.mcp import tools as _tools  # noqa: F401
    from mealie.mcp.consent import router as consent_router

    app.include_router(consent_router)
    host = urlsplit(_base_url).netloc
    origin = f"{urlsplit(_base_url).scheme}://{host}"
    sdk_app = mcp.streamable_http_app(
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(
            allowed_hosts=[host, "localhost", "localhost:*", "127.0.0.1:*", "testserver"],
            allowed_origins=[origin],
        ),
    )
    # Browser-based clients (e.g. MCP Inspector) preflight discovery requests
    cors_methods = ["GET", "OPTIONS"]
    for path, handler in (
        ("/.well-known/oauth-authorization-server", authorization_metadata),
        (_metadata_path("oauth-authorization-server", "/oauth"), authorization_metadata),
        (_metadata_path("oauth-protected-resource", "/mcp"), protected_resource_metadata),
    ):
        app.router.routes.append(Route(path, endpoint=cors_middleware(handler, cors_methods), methods=cors_methods))
    for route in sdk_app.routes:
        if not isinstance(route, Route) or route.path in {
            "/.well-known/oauth-authorization-server",
            "/.well-known/oauth-protected-resource/mcp",
        }:
            continue
        public_path = (
            "/oauth" + route.path if route.path in {"/authorize", "/token", "/register", "/revoke"} else route.path
        )
        app.router.routes.append(
            Route(public_path, endpoint=McpRouteAdapter(sdk_app, route.path, public_path), methods=route.methods)
        )
    # Clients probe other discovery paths (openid-configuration, root protected resource) and
    # need a 404 to fall back from, not the SPA's HTML page
    app.router.routes.append(Route("/.well-known/{path:path}", endpoint=_well_known_not_found, methods=cors_methods))
