from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from mealie.core import security
from mealie.core.security import authenticate_user
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.routes.routers import UserAPIRouter
from mealie.schema.user import UserInDB
from mealie.services.events import create_user_event
from sqlalchemy.orm.session import Session

public_router = APIRouter(prefix="/api/auth", tags=["Authentication"])
user_router = UserAPIRouter(prefix="/api/auth", tags=["Authentication"])


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

    user: UserInDB = authenticate_user(session, email, password)

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
async def refresh_token(current_user: UserInDB = Depends(get_current_user)):
    """ Use a valid token to get another token"""
    access_token = security.create_access_token(data=dict(sub=current_user.email))
    return {"access_token": access_token, "token_type": "bearer"}
