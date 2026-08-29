from datetime import timedelta
from typing import Annotated, Any

import jwt
from fastapi import APIRouter, Depends, Header, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from jwt.exceptions import PyJWTError
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from starlette.datastructures import URLPath

from mealie.core import root_logger, security
from mealie.core.config import get_app_settings
from mealie.core.dependencies import get_auth_token, get_current_user
from mealie.core.exceptions import MissingClaimException, UserLockedOut
from mealie.core.security.providers.reverse_proxy_provider import ReverseProxyProvider
from mealie.core.security.security import get_auth_provider
from mealie.db.db_setup import generate_session
from mealie.lang import get_locale_provider
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.user import PrivateUser
from mealie.schema.user.auth import CredentialsRequestForm, NativeOIDCTokenRequest, OIDCNativeConfig

from .auth_cache import AuthCache

public_router = APIRouter(tags=["Users: Authentication"])
user_router = UserAPIRouter(tags=["Users: Authentication"])
logger = root_logger.get_logger("auth")


settings = get_app_settings()
oauth = None
if settings.OIDC_READY:
    from authlib.integrations.starlette_client import OAuth

    oauth = OAuth(cache=AuthCache())
    scope = None
    if settings.OIDC_SCOPES_OVERRIDE:
        scope = settings.OIDC_SCOPES_OVERRIDE
    else:
        groups_claim = settings.OIDC_GROUPS_CLAIM if settings.OIDC_REQUIRES_GROUP_CLAIM else ""
        scope = f"openid email profile {groups_claim}"
    client_args: dict[str, Any] = {"scope": scope.rstrip()}
    if settings.OIDC_CLIENT_TIMEOUT != "default":
        client_args["timeout"] = settings.OIDC_CLIENT_TIMEOUT if settings.OIDC_CLIENT_TIMEOUT != "None" else None
    if settings.OIDC_TLS_CACERTFILE:
        client_args["verify"] = settings.OIDC_TLS_CACERTFILE

    oauth.register(
        "oidc",
        client_id=settings.OIDC_CLIENT_ID,
        client_secret=settings.OIDC_CLIENT_SECRET,
        server_metadata_url=settings.OIDC_CONFIGURATION_URL,
        client_kwargs=client_args,
        code_challenge_method="S256",
    )


SESSION_COOKIE_NAME = "mealie.access_token"


def request_is_https(request: Request) -> bool:
    """Whether the browser reached Mealie over HTTPS.

    `request.url.scheme` only reflects the browser's own connection when uvicorn's proxy-header
    handling trusted the proxy, which it stops doing as soon as an admin narrows `HOST_IP` from its
    default. Falling back to the header keeps `Secure` — and with it the embedded `SameSite=None`
    path — working behind a proxy Mealie hasn't been told to trust.

    Reading it unverified is safe here in a way it wouldn't be for authorization: it only alters
    attributes on the sender's own cookie in the same response, so forging it achieves nothing beyond
    breaking your own session.
    """
    if request.url.scheme == "https":
        return True

    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    # a chain of proxies appends to this, and the client's own protocol is the first entry
    return forwarded_proto.split(",")[0].strip().lower() == "https"


def session_cookie_attrs(request: Request) -> dict:
    """Cookie attributes that have to match between setting and clearing the session cookie.

    Mealie is sometimes embedded in another site, which needs `SameSite=None` and a partitioned
    cookie. The server can't detect embedding, so the client flags it — and we only honour the flag
    over HTTPS, since browsers reject `SameSite=None` without `Secure`.
    """
    secure = request_is_https(request)
    embedded = secure and request.headers.get("x-mealie-embedded", "").lower() == "true"

    return {
        "path": "/",
        "secure": secure,
        "samesite": "none" if embedded else "lax",
        "partitioned": embedded,
    }


def set_session_cookie(response: Response, request: Request, token: str, expires_in: timedelta, remember_me: bool):
    """Sends the session cookie from the server instead of letting the client write it.

    Safari caps any cookie created through `document.cookie` at seven days, whatever max-age it asks
    for, which silently truncated every iOS session regardless of TOKEN_TIME. Cookies that arrive on
    a Set-Cookie header aren't subject to that cap.
    """
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        # Remember-me decides whether the cookie outlives the browser session. Omitting max-age makes
        # it a session cookie; the token is valid for TOKEN_TIME either way.
        max_age=int(expires_in.total_seconds()) if remember_me else None,
        # The SPA reads this to set its Authorization header, so it can't be HttpOnly yet.
        httponly=False,
        **session_cookie_attrs(request),
    )


class MealieAuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    """seconds until the token expires, so clients can refresh before it does"""

    @classmethod
    def respond(cls, token: str, expires_in: timedelta, token_type: str = "bearer") -> dict:
        return cls(
            access_token=token,
            token_type=token_type,
            expires_in=int(expires_in.total_seconds()),
        ).model_dump()


@public_router.post("/token")
def get_token(
    request: Request,
    response: Response,
    data: CredentialsRequestForm = Depends(),
    session: Session = Depends(generate_session),
):
    if "x-forwarded-for" in request.headers:
        ip = request.headers["x-forwarded-for"]
        if "," in ip:  # if there are multiple IPs, the first one is canonically the true client
            ip = str(ip.split(",")[0])
    else:
        # request.client should never be null, except sometimes during testing
        ip = request.client.host if request.client else "unknown"

    try:
        auth_provider = get_auth_provider(session, data)
        auth = auth_provider.authenticate()
    except UserLockedOut as e:
        logger.error(f"User is locked out from {ip}")
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="User is locked out") from e

    if not auth:
        logger.error(f"Incorrect username or password from {ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    access_token, duration = auth
    set_session_cookie(response, request, access_token, duration, data.remember_me)
    return MealieAuthToken.respond(access_token, duration)


@public_router.get("/oauth")
async def oauth_login(request: Request):
    if not oauth:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not initialize OAuth client",
        )
    client = oauth.create_client("oidc")
    redirect_url = None
    if not settings.PRODUCTION:
        # in development, we want to redirect to the frontend
        redirect_url = "http://localhost:3000/login"
    else:
        # Prioritize User Configuration over Request Headers.
        if not settings.is_default_base_url:
            base = settings.BASE_URL or request.base_url
        else:
            base = request.base_url
        redirect_url = URLPath("/login").make_absolute_url(base)

    response: RedirectResponse = await client.authorize_redirect(request, redirect_url)
    return response


@public_router.get("/oauth/callback")
async def oauth_callback(request: Request, response: Response, session: Session = Depends(generate_session)):
    if not oauth:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not initialize OAuth client",
        )
    client = oauth.create_client("oidc")

    token = await client.authorize_access_token(request)

    from mealie.core.security.providers.openid_provider import OpenIDProvider

    auth = None
    try:
        auth_provider = OpenIDProvider(session, token["userinfo"])
        auth = auth_provider.authenticate()
    except MissingClaimException:
        try:
            logger.debug("[OIDC] Claims not present in the ID token, pulling user info")
            userinfo = await client.userinfo(token=token)
            auth_provider = OpenIDProvider(session, userinfo, use_default_groups=True)
            auth = auth_provider.authenticate()
        except MissingClaimException:
            logger.error("[OIDC] Required claims not present in ID token or userinfo endpoint")
            auth = None

    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    access_token, duration = auth
    set_session_cookie(response, request, access_token, duration, settings.OIDC_REMEMBER_ME)
    return MealieAuthToken.respond(access_token, duration)


@public_router.get("/oauth/native/config", response_model=OIDCNativeConfig)
async def oauth_native_config():
    """Return the parameters a native client needs to build its own OIDC authorization request."""
    if not settings.OIDC_READY or not oauth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OIDC is not configured",
        )

    client = oauth.create_client("oidc")
    metadata = await client.load_server_metadata()
    return OIDCNativeConfig(
        authorization_endpoint=metadata["authorization_endpoint"],
        client_id=client.client_id,
        scope=client.client_kwargs.get("scope", "openid email profile"),
    )


@public_router.post("/oauth/native/token")
async def oauth_native_token(
    request: Request,
    response: Response,
    data: NativeOIDCTokenRequest,
    session: Session = Depends(generate_session),
):
    """Exchange a native client's authorization code for a Mealie token.

    The native client owns PKCE and state, so the exchange happens server-side without a browser
    session cookie. This lets passkey-capable system-browser logins (e.g. Pocket ID) work, which
    the cookie-coupled web callback cannot support.
    """
    if not settings.OIDC_READY or not oauth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OIDC is not configured",
        )

    from authlib.integrations.starlette_client import OAuthError

    client = oauth.create_client("oidc")
    try:
        token = await client.fetch_access_token(
            code=data.code,
            code_verifier=data.code_verifier,
            redirect_uri=data.redirect_uri,
        )
        userinfo = await client.parse_id_token(token, nonce=data.nonce)
    except OAuthError as e:
        logger.error("[OIDC] Native token exchange failed: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from e

    from mealie.core.security.providers.openid_provider import OpenIDProvider

    auth = None
    try:
        auth_provider = OpenIDProvider(session, userinfo)
        auth = auth_provider.authenticate()
    except MissingClaimException:
        try:
            logger.debug("[OIDC] Claims not present in the id_token, pulling user info")
            userinfo = await client.userinfo(token=token)
            auth_provider = OpenIDProvider(session, userinfo, use_default_groups=True)
            auth = auth_provider.authenticate()
        except MissingClaimException:
            logger.error("[OIDC] Required claims not present in ID token or userinfo endpoint")
            auth = None

    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    access_token, duration = auth
    set_session_cookie(response, request, access_token, duration, settings.OIDC_REMEMBER_ME)
    return MealieAuthToken.respond(access_token, duration)


@public_router.get("/reverse-proxy")
async def reverse_proxy_login(
    request: Request,
    response: Response,
    session: Session = Depends(generate_session),
):
    """Authenticate a user using a username forwarded by a trusted reverse proxy header"""
    if not settings.REVERSE_PROXY_AUTH_READY:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    username = request.headers.get(settings.REVERSE_PROXY_AUTH_HEADER)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    auth_provider = ReverseProxyProvider(session, username)
    auth = auth_provider.authenticate()
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    access_token, duration = auth
    set_session_cookie(response, request, access_token, duration, remember_me=True)
    return MealieAuthToken.respond(access_token, duration)


@user_router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    current_user: PrivateUser = Depends(get_current_user),
    token: str = Depends(get_auth_token),
):
    """Exchange a valid session token for a fresh one.

    The new token carries over the remember-me choice recorded on the old one, so refreshing doesn't
    downgrade a remembered session to one that dies with the browser.
    """
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=[security.ALGORITHM])
    except PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from e

    if payload.get("long_token"):
        # A long-lived API token is revocable by its owner; exchanging one for a session token would
        # produce a credential that survives that revocation.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API tokens cannot be exchanged for a session token",
        )

    remember_me = bool(payload.get("rme", False))
    access_token, duration = security.create_access_token({"sub": str(current_user.id), "rme": remember_me})
    set_session_cookie(response, request, access_token, duration, remember_me)
    return MealieAuthToken.respond(access_token, duration)


@user_router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    accept_language: Annotated[str | None, Header()] = None,
):
    # Clearing a cookie only works when the attributes match the ones it was set with, which the old
    # bare delete_cookie() call didn't manage for embedded (partitioned, SameSite=None) deployments.
    response.set_cookie(SESSION_COOKIE_NAME, "", max_age=0, expires=0, **session_cookie_attrs(request))

    translator = get_locale_provider(accept_language)
    return {"message": translator.t("notifications.logged-out")}
