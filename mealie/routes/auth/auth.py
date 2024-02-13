from datetime import timedelta

from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from mealie.core import root_logger, security
from mealie.core.config import get_app_settings
from mealie.core.dependencies import get_current_user
from mealie.core.security import authenticate_user
from mealie.core.security.security import UserLockedOut
from mealie.db.db_setup import generate_session
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.user import PrivateUser

public_router = APIRouter(tags=["Users: Authentication"])
user_router = UserAPIRouter(tags=["Users: Authentication"])
logger = root_logger.get_logger("auth")

remember_me_duration = timedelta(days=14)


class CustomOAuth2Form(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form(None, pattern="password"),
        username: str = Form(...),
        password: str = Form(...),
        remember_me: bool = Form(False),
        scope: str = Form(""),
        client_id: str | None = Form(None),
        client_secret: str | None = Form(None),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.remember_me = remember_me
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


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
    data: CustomOAuth2Form = Depends(),
    session: Session = Depends(generate_session),
):
    settings = get_app_settings()

    email = data.username
    password = data.password
    if "x-forwarded-for" in request.headers:
        ip = request.headers["x-forwarded-for"]
        if "," in ip:  # if there are multiple IPs, the first one is canonically the true client
            ip = str(ip.split(",")[0])
    else:
        # request.client should never be null, except sometimes during testing
        ip = request.client.host if request.client else "unknown"

    try:
        user = authenticate_user(session, email, password)  # type: ignore
    except UserLockedOut as e:
        logger.error(f"User is locked out from {ip}")
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="User is locked out") from e

    if not user:
        logger.error(f"Incorrect username or password from {ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    duration = timedelta(hours=settings.TOKEN_TIME)
    if data.remember_me and remember_me_duration > duration:
        duration = remember_me_duration

    access_token = security.create_access_token(dict(sub=str(user.id)), duration)  # type: ignore

    response.set_cookie(
        key="mealie.access_token",
        value=access_token,
        httponly=True,
        max_age=duration.seconds if duration else None,
    )

    return MealieAuthToken.respond(access_token)


@user_router.get("/refresh")
async def refresh_token(current_user: PrivateUser = Depends(get_current_user)):
    """Use a valid token to get another token"""
    access_token = security.create_access_token(data=dict(sub=str(current_user.id)))
    return MealieAuthToken.respond(access_token)
