from datetime import timedelta

from mealie.core.security import verify_password
from mealie.db.db_setup import generate_session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from mealie.routes.deps import manager, query_user
from mealie.schema.snackbar import SnackResponse
from mealie.schema.user import UserInDB
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/token")
def get_token(
    data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(generate_session),
):
    email = data.username
    password = data.password

    user: UserInDB = query_user(email, session)
    if not user:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif not verify_password(password, user.password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=email), expires=timedelta(hours=2))
    return SnackResponse.success(
        "User Successfully Logged In",
        {"access_token": access_token, "token_type": "bearer"},
    )


@router.post("/token/long")
def get_long_token(
    data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(generate_session),
):
    """Get an Access Token for 1 day"""
    email = data.username
    password = data.password

    user: UserInDB = query_user(email, session)
    if not user:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif not verify_password(password, user.password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=email), expires=timedelta(days=1))
    return SnackResponse.success(
        "User Successfully Logged In",
        {"access_token": access_token, "token_type": "bearer"},
    )


@router.get("/refresh")
async def refresh_token(current_user: UserInDB = Depends(manager)):
    """ Use a valid token to get another token"""
    access_token = manager.create_access_token(data=dict(sub=current_user.email), expires=timedelta(hours=1))
    return {"access_token": access_token, "token_type": "bearer"}
