from datetime import timedelta

from core.security import verify_password
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from routes.deps import manager, query_user
from schema.user import UserInDB
from sqlalchemy.orm.session import Session
from schema.snackbar import SnackResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/token")
def token(
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

    access_token = manager.create_access_token(
        data=dict(sub=email), expires=timedelta(hours=2)
    )
    return SnackResponse.success("User Successfully Logged In", {"access_token": access_token, "token_type": "bearer"})
