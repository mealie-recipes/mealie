from datetime import timedelta

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm.session import Session
from starlette.datastructures import URLPath

from mealie.core import root_logger, security
from mealie.core.config import get_app_settings
from mealie.core.dependencies import get_current_user
from mealie.core.exceptions import MissingClaimException, UserLockedOut
from mealie.core.security.providers.openid_provider import OpenIDProvider
from mealie.core.security.security import get_auth_provider
from mealie.db.db_setup import generate_session
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.user import PrivateUser
from mealie.schema.user.auth import CredentialsRequestForm

public_router = APIRouter(tags=["Users: Authentication"])
user_router = UserAPIRouter(tags=["Users: Authentication"])
logger = root_logger.get_logger("auth")

remember_me_duration = timedelta(days=14)

settings = get_app_settings()
if settings.OIDC_READY:
    oauth = OAuth()
    scope = None
    if settings.OIDC_SCOPES_OVERRIDE:
        scope = settings.OIDC_SCOPES_OVERRIDE
    else:
        groups_claim = settings.OIDC_GROUPS_CLAIM if settings.OIDC_REQUIRES_GROUP_CLAIM else ""
        scope = f"openid email profile {groups_claim}"
    client_args = {"scope": scope.rstrip()}
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


class MealieAuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

    @classmethod
    def respond(cls, token: str, token_type: str = "bearer") -> dict:
        return cls(access_token=token, token_type=token_type).model_dump()


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

    expires_in = duration.total_seconds() if duration else None
    response.set_cookie(
        key="mealie.access_token",
        value=access_token,
        httponly=True,
        max_age=expires_in,
        secure=settings.PRODUCTION,
    )

    return MealieAuthToken.respond(access_token)


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
        redirect_url = URLPath("/login").make_absolute_url(request.base_url)

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

    auth = None
    try:
        auth_provider = OpenIDProvider(session, token["userinfo"])
        auth = auth_provider.authenticate()
    except MissingClaimException:
        try:
            logger.debug("[OIDC] Claims not present in the ID token, pulling user info")
            userinfo = await client.userinfo(token=token)
            auth_provider = OpenIDProvider(session, userinfo)
            auth = auth_provider.authenticate()
        except MissingClaimException:
            auth = None

    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    access_token, duration = auth

    expires_in = duration.total_seconds() if duration else None

    response.set_cookie(
        key="mealie.access_token",
        value=access_token,
        httponly=True,
        max_age=expires_in,
        secure=settings.PRODUCTION,
    )

    return MealieAuthToken.respond(access_token)


@user_router.get("/refresh")
async def refresh_token(current_user: PrivateUser = Depends(get_current_user)):
    """Use a valid token to get another token"""
    access_token = security.create_access_token(data={"sub": str(current_user.id)})
    return MealieAuthToken.respond(access_token)


@user_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("mealie.access_token")
    return {"message": "Logged out"}
