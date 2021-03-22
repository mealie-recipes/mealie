from datetime import timedelta

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from mealie.core import security
from mealie.core.security import authenticate_user, verify_password
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.snackbar import SnackResponse
from mealie.schema.user import UserInDB
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/token/long")
@router.post("/token")
def get_token(
    data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(generate_session),
):
    email = data.username
    password = data.password

    user = authenticate_user(session, email, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(dict(sub=email), timedelta(hours=2))
    return SnackResponse.success(
        "User Successfully Logged In",
        {"access_token": access_token, "token_type": "bearer"},
    )


@router.get("/refresh")
async def refresh_token(current_user: UserInDB = Depends(get_current_user)):
    """ Use a valid token to get another token"""
    access_token = security.create_access_token(data=dict(sub=current_user.email), expires_delta=timedelta(hours=1))
    return {"access_token": access_token, "token_type": "bearer"}
