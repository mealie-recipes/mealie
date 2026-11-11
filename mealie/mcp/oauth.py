"""Persistent OAuth provider for the embedded MCP server.

The MCP SDK owns protocol parsing, redirect URI matching, PKCE verification,
and OAuth response formatting. This module owns Mealie grants and token storage.
"""

import base64
import hashlib
import ipaddress
import json
import logging
import secrets
import socket
import time
from datetime import UTC, datetime, timedelta
from urllib.parse import urlsplit, urlunsplit

import anyio.to_thread
import httpx
from cryptography.fernet import Fernet, InvalidToken
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    OAuthAuthorizationServerProvider,
    RefreshToken,
    RegistrationError,
    TokenError,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from pydantic import AnyUrl, ValidationError
from sqlalchemy import update
from sqlalchemy.orm import Session

from mealie.core.config import PRODUCTION, TESTING, get_app_settings
from mealie.db.db_setup import SessionLocal
from mealie.db.models.server.mcp import (
    McpAuthorizationCode,
    McpAuthorizationRequest,
    McpClient,
    McpGrant,
    McpSetting,
    McpToken,
)
from mealie.db.models.users.users import User

SCOPES = (
    "profile:read",
    "recipes:read",
    "recipes:write",
    "mealplans:read",
    "mealplans:write",
    "shopping:read",
    "shopping:write",
)
ACCESS_LIFETIME = timedelta(minutes=15)
REFRESH_LIFETIME = timedelta(days=30)
CODE_LIFETIME = timedelta(minutes=5)
REQUEST_LIFETIME = timedelta(minutes=10)
# A client that retries a refresh, or two processes sharing credentials, can present a
# refresh token again moments after it was rotated. That is not theft, so don't revoke.
REFRESH_REUSE_GRACE = timedelta(seconds=60)
CLIENT_METADATA_TTL = 300
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
logger = logging.getLogger("mealie.mcp")


class _Session:
    """Avoid generator context managers rewriting frozen SDK OAuth exceptions."""

    def __enter__(self) -> Session:
        self.session = SessionLocal()
        return self.session

    def __exit__(self, *_):
        self.session.close()


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def digest(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def _client_cipher() -> Fernet:
    key = hashlib.sha256(get_app_settings().SECRET.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def public_base_url() -> str:
    """Return a stable, externally configured origin and optional install prefix."""
    value = get_app_settings().BASE_URL.rstrip("/")
    parts = urlsplit(value)
    if (
        parts.scheme not in {"http", "https"}
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
        or "//" in parts.path
    ):
        raise ValueError("BASE_URL must be an absolute HTTP or HTTPS URL without credentials or a query")
    return value


def validate_enablement_url() -> str:
    url = public_base_url()
    parts = urlsplit(url)
    loopback = parts.hostname in {"localhost", "127.0.0.1", "::1"}
    if parts.scheme != "https" and (not loopback or (PRODUCTION and not TESTING)):
        raise ValueError("Set BASE_URL to the public HTTPS Mealie URL before enabling MCP")
    return url + "/mcp"


def mcp_url() -> str:
    return public_base_url() + "/mcp"


def canonical_resource(value: str | None) -> str | None:
    """Map the resource indicators clients send for this server onto the MCP URL.

    Clients variously omit the RFC 8707 resource, add a trailing slash, or send the
    site origin. Anything naming a different resource returns None.
    """
    target = mcp_url()
    if value is None:
        return target
    return target if value.rstrip("/") in {target, public_base_url()} else None


def known_scopes(requested: str | None) -> list[str]:
    """Drop scopes Mealie does not define (openid, offline_access, ...); RFC 6749 section 3.3 allows granting fewer."""
    return [scope for scope in (requested or "").split() if scope in SCOPES]


def issuer_url() -> str:
    return public_base_url() + "/oauth"


def mcp_enabled(session: Session) -> bool:
    row = session.get(McpSetting, 1)
    if not row or not row.enabled:
        return False
    try:
        validate_enablement_url()
    except ValueError:
        return False
    return True


def _active_user(session: Session, grant: McpGrant) -> User | None:
    user = session.get(User, grant.user_id)
    if not user or user.household_id != grant.household_id or user.locked_at:
        return None
    if user.tokens_valid_after and (not grant.created_at or grant.created_at < user.tokens_valid_after):
        return None
    return user


def set_mcp_enabled(session: Session, enabled: bool) -> None:
    row = session.get(McpSetting, 1)
    if row is None:
        row = McpSetting(id=1, enabled=False)
        session.add(row)
    if row.enabled and not enabled:
        now = utcnow()
        session.query(McpGrant).filter(McpGrant.revoked_at.is_(None)).update({McpGrant.revoked_at: now})
        session.query(McpToken).filter(McpToken.revoked_at.is_(None)).update({McpToken.revoked_at: now})
    row.enabled = enabled
    session.commit()


def _redirect_allowed(uri: str, application_type: str | None) -> bool:
    parts = urlsplit(uri)
    if not parts.scheme or not parts.hostname or parts.fragment or parts.username or parts.password:
        return False
    if parts.scheme == "https":
        return True
    if application_type == "native" and parts.scheme == "http" and parts.hostname in LOOPBACK_HOSTS:
        return True
    # Native custom-scheme callbacks do not send credentials to a network host.
    return application_type == "native" and parts.scheme not in {"http", "https"}


def _loopback_redirect_registered(uri: str, registered: list[AnyUrl]) -> bool:
    """RFC 8252 section 7.3: loopback redirects may use any port the native app chose at runtime."""
    parts = urlsplit(uri)
    if parts.scheme != "http" or parts.hostname not in LOOPBACK_HOSTS or parts.fragment or parts.username:
        return False
    for item in registered:
        other = urlsplit(str(item))
        if (other.scheme, other.hostname, other.path, other.query) == (
            parts.scheme,
            parts.hostname,
            parts.path,
            parts.query,
        ):
            return True
    return False


class McpClientInformation(OAuthClientInformationFull):
    """Client metadata with loopback redirect matching that ignores the port."""

    def validate_redirect_uri(self, redirect_uri: AnyUrl | None) -> AnyUrl:
        if redirect_uri is not None and _loopback_redirect_registered(str(redirect_uri), self.redirect_uris or []):
            return redirect_uri
        return super().validate_redirect_uri(redirect_uri)

    def validate_scope(self, requested_scope: str | None) -> list[str] | None:
        scopes = known_scopes(requested_scope)
        return super().validate_scope(" ".join(scopes)) if scopes else None


def _validate_client(client: OAuthClientInformationFull) -> None:
    if client.client_name and len(client.client_name) > 255:
        raise RegistrationError("invalid_client_metadata", "Client name is too long")
    if not client.redirect_uris or len(client.redirect_uris) > 10:
        raise RegistrationError("invalid_redirect_uri", "One to ten redirect URIs are required")
    if any(not _redirect_allowed(str(uri), client.application_type) for uri in client.redirect_uris):
        raise RegistrationError(
            "invalid_redirect_uri", "Redirect URI must use HTTPS or a native loopback/custom scheme"
        )


async def _fetch_client_metadata(client_id: str) -> OAuthClientInformationFull | None:
    """Resolve a CIMD URL with bounded, public-only network access."""
    try:
        if len(client_id) > 2048:
            return None
        parts = urlsplit(client_id)
        if (
            parts.scheme != "https"
            or not parts.hostname
            or parts.username
            or parts.password
            or parts.fragment
            or parts.port not in (None, 443)
        ):
            return None
        addresses = await anyio.to_thread.run_sync(
            lambda: socket.getaddrinfo(parts.hostname, 443, type=socket.SOCK_STREAM)
        )
        if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
            return None
        address = ipaddress.ip_address(addresses[0][4][0])
        pinned_host = f"[{address}]" if address.version == 6 else str(address)
        pinned_url = urlunsplit(("https", pinned_host, parts.path, parts.query, ""))
        async with httpx.AsyncClient(timeout=5, follow_redirects=False, trust_env=False) as client:
            request = client.build_request(
                "GET",
                pinned_url,
                headers={"Accept": "application/json", "Host": parts.netloc},
                extensions={"sni_hostname": parts.hostname},
            )
            response = await client.send(request, stream=True)
            try:
                if response.status_code != 200:
                    return None
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > 65536:
                        return None
            finally:
                await response.aclose()
        if not content:
            return None
        payload = json.loads(content)
        if not isinstance(payload, dict) or payload.get("client_id") != client_id:
            return None
        methods = payload.get("token_endpoint_auth_methods_supported")
        if methods is not None:
            if not isinstance(methods, list) or "none" not in methods:
                return None
        elif payload.get("token_endpoint_auth_method", "none") != "none":
            return None
        result = McpClientInformation.model_validate(
            {
                **payload,
                "client_id": client_id,
                "client_secret": None,
                "token_endpoint_auth_method": "none",
                "scope": " ".join(known_scopes(payload.get("scope")) or SCOPES),
                # Documents that omit application_type but use loopback or custom-scheme
                # callbacks (as in the MCP spec's own example) are native apps
                "application_type": payload.get("application_type")
                or (
                    "native"
                    if any(not str(uri).startswith("https://") for uri in payload.get("redirect_uris") or [])
                    else None
                ),
            }
        )
        _validate_client(result)
        return result
    except OSError, httpx.HTTPError, ValueError, ValidationError, RegistrationError:
        return None


_client_metadata_cache: dict[str, tuple[float, OAuthClientInformationFull]] = {}


async def _cached_client_metadata(client_id: str) -> OAuthClientInformationFull | None:
    """CIMD documents are fetched on every OAuth call otherwise; a slow or failing fetch would break refreshes."""
    cached = _client_metadata_cache.get(client_id)
    if cached and cached[0] > time.monotonic():
        return cached[1]
    client = await _fetch_client_metadata(client_id)
    if client:
        _client_metadata_cache[client_id] = (time.monotonic() + CLIENT_METADATA_TTL, client)
    elif cached:
        return cached[1]
    return client


class MealieOAuthProvider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        with _Session() as session:
            row = session.query(McpClient).filter_by(client_id=client_id).one_or_none()
            if row:
                try:
                    metadata = _client_cipher().decrypt(row.metadata_json.encode())
                except InvalidToken:
                    return None
                return McpClientInformation.model_validate_json(metadata)
        return await _cached_client_metadata(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        _validate_client(client_info)
        client_info = client_info.model_copy(update={"scope": " ".join(known_scopes(client_info.scope) or SCOPES)})
        with _Session() as session:
            if not mcp_enabled(session):
                raise RegistrationError("invalid_client_metadata", "MCP is disabled")
            metadata = _client_cipher().encrypt(client_info.model_dump_json().encode()).decode()
            session.add(
                McpClient(
                    client_id=client_info.client_id,
                    client_name=client_info.client_name,
                    metadata_json=metadata,
                )
            )
            session.commit()

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        resource = canonical_resource(params.resource)
        if resource is None:
            raise AuthorizeError("invalid_target", "The resource must be this Mealie MCP URL")
        scopes = params.scopes or list(SCOPES)
        if not set(scopes).issubset(SCOPES):
            raise AuthorizeError("invalid_scope", "Unsupported MCP scope")
        request_secret = secrets.token_urlsafe(32)
        with _Session() as session:
            if not mcp_enabled(session):
                raise AuthorizeError("temporarily_unavailable", "MCP is disabled")
            session.add(
                McpAuthorizationRequest(
                    request_hash=digest(request_secret),
                    client_id=client.client_id,
                    params_json=params.model_copy(update={"scopes": scopes, "resource": resource}).model_dump_json(),
                    expires_at=utcnow() + REQUEST_LIFETIME,
                )
            )
            session.commit()
        logger.info("MCP authorization requested by client %s", client.client_id)
        return f"{public_base_url()}/oauth/consent?request={request_secret}"

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        with _Session() as session:
            row = session.query(McpAuthorizationCode).filter_by(code_hash=digest(authorization_code)).one_or_none()
            if not row or row.client_id != client.client_id or row.used_at or row.expires_at <= utcnow():
                return None
            grant = session.get(McpGrant, row.grant_id)
            if not grant or grant.revoked_at or not mcp_enabled(session):
                return None
            return AuthorizationCode.model_validate_json(row.params_json).model_copy(
                update={"code": authorization_code}
            )

    def _issue_tokens(self, session: Session, grant: McpGrant, scopes: list[str], family_id: str) -> OAuthToken:
        access = secrets.token_urlsafe(48)
        refresh = secrets.token_urlsafe(48)
        now = utcnow()
        session.add_all(
            [
                McpToken(
                    token_hash=digest(access),
                    grant_id=grant.id,
                    family_id=family_id,
                    kind="access",
                    scopes_json=json.dumps(scopes),
                    expires_at=now + ACCESS_LIFETIME,
                ),
                McpToken(
                    token_hash=digest(refresh),
                    grant_id=grant.id,
                    family_id=family_id,
                    kind="refresh",
                    scopes_json=json.dumps(scopes),
                    expires_at=now + REFRESH_LIFETIME,
                ),
            ]
        )
        session.commit()
        return OAuthToken(
            access_token=access,
            refresh_token=refresh,
            expires_in=int(ACCESS_LIFETIME.total_seconds()),
            scope=" ".join(scopes),
        )

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        if authorization_code.resource != mcp_url():
            raise TokenError("invalid_target", "Wrong resource")
        with _Session() as session:
            row = session.query(McpAuthorizationCode).filter_by(code_hash=digest(authorization_code.code)).one_or_none()
            if not row or row.used_at or row.expires_at <= utcnow() or row.client_id != client.client_id:
                raise TokenError("invalid_grant", "Authorization code expired or used")
            result = session.execute(
                update(McpAuthorizationCode)
                .where(McpAuthorizationCode.id == row.id, McpAuthorizationCode.used_at.is_(None))
                .values(used_at=utcnow())
            )
            if result.rowcount != 1:
                raise TokenError("invalid_grant", "Authorization code already used")
            grant = session.get(McpGrant, row.grant_id)
            if (
                not grant
                or grant.revoked_at
                or not mcp_enabled(session)
                or not set(authorization_code.scopes).issubset(json.loads(grant.scopes_json))
            ):
                raise TokenError("invalid_grant", "Grant revoked")
            if not _active_user(session, grant):
                raise TokenError("invalid_grant", "Account unavailable")
            tokens = self._issue_tokens(session, grant, authorization_code.scopes, secrets.token_hex(32))
            logger.info("MCP authorization code exchanged for grant %s", grant.id)
            return tokens

    async def load_refresh_token(self, client: OAuthClientInformationFull, refresh_token: str) -> RefreshToken | None:
        with _Session() as session:
            row = session.query(McpToken).filter_by(token_hash=digest(refresh_token), kind="refresh").one_or_none()
            if not row or row.revoked_at or row.expires_at <= utcnow():
                return None
            grant = session.get(McpGrant, row.grant_id)
            if not grant or grant.revoked_at or grant.client_id != client.client_id or not mcp_enabled(session):
                return None
            if not _active_user(session, grant):
                return None
            return RefreshToken(
                token=refresh_token,
                client_id=client.client_id,
                scopes=json.loads(grant.scopes_json),
                expires_at=int(row.expires_at.replace(tzinfo=UTC).timestamp()),
                resource=mcp_url(),
                subject=str(grant.user_id),
            )

    async def exchange_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: RefreshToken, scopes: list[str]
    ) -> OAuthToken:
        with _Session() as session:
            row = (
                session.query(McpToken).filter_by(token_hash=digest(refresh_token.token), kind="refresh").one_or_none()
            )
            if not row:
                raise TokenError("invalid_grant", "Unknown refresh token")
            if row.used_at and utcnow() - row.used_at < REFRESH_REUSE_GRACE:
                raise TokenError("invalid_grant", "Refresh token already rotated")
            if row.used_at:
                session.query(McpToken).filter_by(family_id=row.family_id).update({McpToken.revoked_at: utcnow()})
                grant = session.get(McpGrant, row.grant_id)
                if grant:
                    grant.revoked_at = utcnow()
                session.commit()
                logger.warning("MCP refresh token reuse revoked grant %s", row.grant_id)
                raise TokenError("invalid_grant", "Refresh token reuse detected")
            if row.revoked_at or row.expires_at <= utcnow():
                raise TokenError("invalid_grant", "Refresh token expired or revoked")
            grant = session.get(McpGrant, row.grant_id)
            if not grant or grant.revoked_at or grant.client_id != client.client_id or not mcp_enabled(session):
                raise TokenError("invalid_grant", "Grant revoked")
            if not _active_user(session, grant):
                raise TokenError("invalid_grant", "Account unavailable")
            # The user can change a connection's permissions in Mealie, so a refresh may
            # pick up scopes the original token never had; it can't exceed the grant
            if not set(scopes).issubset(json.loads(grant.scopes_json)):
                raise TokenError("invalid_scope", "Scope not granted to this connection")
            result = session.execute(
                update(McpToken).where(McpToken.id == row.id, McpToken.used_at.is_(None)).values(used_at=utcnow())
            )
            if result.rowcount != 1:
                # A concurrent request rotated this token between our read and update
                session.rollback()
                raise TokenError("invalid_grant", "Refresh token already rotated")
            tokens = self._issue_tokens(session, grant, scopes, row.family_id)
            logger.info("MCP refresh token rotated for grant %s", grant.id)
            return tokens

    async def load_access_token(self, token: str) -> AccessToken | None:
        with _Session() as session:
            row = session.query(McpToken).filter_by(token_hash=digest(token), kind="access").one_or_none()
            if not row or row.revoked_at or row.expires_at <= utcnow() or not mcp_enabled(session):
                return None
            grant = session.get(McpGrant, row.grant_id)
            if not grant or grant.revoked_at:
                return None
            user = _active_user(session, grant)
            if not user:
                return None
            # Permissions come from the grant, not the token, so edits in Connected apps apply immediately
            return AccessToken(
                token=token,
                client_id=grant.client_id,
                scopes=json.loads(grant.scopes_json),
                expires_at=int(row.expires_at.replace(tzinfo=UTC).timestamp()),
                resource=mcp_url(),
                subject=str(user.id),
                claims={"iss": issuer_url(), "household_id": str(grant.household_id), "grant_id": grant.id},
            )

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        with _Session() as session:
            row = session.query(McpToken).filter_by(token_hash=digest(token.token)).one_or_none()
            if row:
                session.query(McpToken).filter_by(family_id=row.family_id).update({McpToken.revoked_at: utcnow()})
                session.commit()
                logger.info("MCP token family revoked for grant %s", row.grant_id)
