from datetime import timedelta

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from mealie.core import root_logger, security
from mealie.core.dependencies import get_current_user
from mealie.core.exceptions import UserLockedOut
from mealie.core.security.security import get_auth_provider
from mealie.db.db_setup import generate_session
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.user import PrivateUser
from mealie.schema.user.auth import CredentialsRequestForm

public_router = APIRouter(tags=["Users: Authentication"])
user_router = UserAPIRouter(tags=["Users: Authentication"])
logger = root_logger.get_logger("auth")

remember_me_duration = timedelta(days=14)


class MealieAuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

    @classmethod
    def respond(cls, token: str, token_type: str = "bearer") -> dict:
        return cls(access_token=token, token_type=token_type).model_dump()


@public_router.post("/token")
async def get_token(
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
        auth_provider = get_auth_provider(session, request, data)
        auth = await auth_provider.authenticate()
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
        key="mealie.access_token", value=access_token, httponly=True, max_age=expires_in, expires=expires_in
    )

    return MealieAuthToken.respond(access_token)


@user_router.get("/refresh")
async def refresh_token(current_user: PrivateUser = Depends(get_current_user)):
    """Use a valid token to get another token"""
    access_token = security.create_access_token(data=dict(sub=str(current_user.id)))
    return MealieAuthToken.respond(access_token)
