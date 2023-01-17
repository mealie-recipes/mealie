from datetime import timedelta

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from mealie.core import security
from mealie.core.config import get_app_settings
from mealie.core.dependencies import get_current_user
from mealie.core.security import authenticate_user, authenticate_user_sso
from mealie.core.security.security import UserLockedOut
from mealie.db.db_setup import generate_session
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.user import PrivateUser

public_router = APIRouter(tags=["Users: Authentication"])
user_router = UserAPIRouter(tags=["Users: Authentication"])


class CustomOAuth2Form(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form(None, regex="password"),
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
        return cls(access_token=token, token_type=token_type).dict()


@public_router.post("/token")
def get_token(request: Request, data: CustomOAuth2Form = Depends(), session: Session = Depends(generate_session)):
    settings = get_app_settings()

    if settings.SSO_ENABLED and request.headers.get(settings.SSO_TRUSTED_HEADER_USER, False):
        user = authenticate_user_sso(
            session,
            username=request.headers.get(settings.SSO_TRUSTED_HEADER_USER),
            email=request.headers.get(settings.SSO_TRUSTED_HEADER_EMAIL),
            name=request.headers.get(settings.SSO_TRUSTED_HEADER_NAME),
        )
    else:
        user_identifier = data.username
        password = data.password

        try:
            user = authenticate_user(session, user_identifier, password)  # type: ignore
        except UserLockedOut as e:
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="User is locked out") from e

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    duration = timedelta(days=14) if data.remember_me else None
    access_token = security.create_access_token(dict(sub=str(user.id)), duration)  # type: ignore
    return MealieAuthToken.respond(access_token)


@user_router.get("/refresh")
async def refresh_token(current_user: PrivateUser = Depends(get_current_user)):
    """Use a valid token to get another token"""
    access_token = security.create_access_token(data=dict(sub=str(current_user.id)))
    return MealieAuthToken.respond(access_token)
