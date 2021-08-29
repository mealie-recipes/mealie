from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from mealie.core import security
from mealie.core.dependencies import get_current_user
from mealie.core.security import authenticate_user
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.user import PrivateUser
from mealie.services.events import create_user_event

public_router = APIRouter(tags=["Users: Authentication"])
user_router = UserAPIRouter(tags=["Users: Authentication"])


@public_router.post("/token/long")
@public_router.post("/token")
def get_token(
    background_tasks: BackgroundTasks,
    request: Request,
    data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(generate_session),
):
    email = data.username
    password = data.password

    user: PrivateUser = authenticate_user(session, email, password)

    if not user:
        background_tasks.add_task(
            create_user_event, "Failed Login", f"Username: {email}, Source IP: '{request.client.host}'"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(dict(sub=user.email))
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/refresh")
async def refresh_token(current_user: PrivateUser = Depends(get_current_user)):
    """ Use a valid token to get another token"""
    access_token = security.create_access_token(data=dict(sub=current_user.email))
    return {"access_token": access_token, "token_type": "bearer"}
