from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Form, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from mealie.core import security
from mealie.core.dependencies import get_current_user
from mealie.core.security import authenticate_user
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
        client_id: Optional[str] = Form(None),
        client_secret: Optional[str] = Form(None),
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
def get_token(
    data: CustomOAuth2Form = Depends(),
    session: Session = Depends(generate_session),
):
    email = data.username
    password = data.password

    user: PrivateUser = authenticate_user(session, email, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    duration = timedelta(days=14) if data.remember_me else None
    access_token = security.create_access_token(dict(sub=user.email), duration)
    return MealieAuthToken.respond(access_token)


@user_router.get("/refresh")
async def refresh_token(current_user: PrivateUser = Depends(get_current_user)):
    """Use a valid token to get another token"""
    access_token = security.create_access_token(data=dict(sub=current_user.email))
    return MealieAuthToken.respond(access_token)
