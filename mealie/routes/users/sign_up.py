import uuid

from core.security import get_password_hash
from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from routes.deps import manager
from schema.sign_up import SignUpIn, SignUpOut, SignUpToken
from schema.snackbar import SnackResponse
from schema.user import UserIn, UserInDB
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/users/sign-ups", tags=["User Signup"])


@router.get("", response_model=list[SignUpOut])
async def get_all_open_sign_ups(
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Returns a list of open sign up links """

    all_sign_ups = db.sign_ups.get_all(session)

    return all_sign_ups


@router.post("", response_model=SignUpToken)
async def create_user_sign_up_key(
    key_data: SignUpIn,
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Generates a Random Token that a new user can sign up with """

    if current_user.admin:
        sign_up = {"token": str(uuid.uuid1().hex), "name": key_data.name}
        db_entry = db.sign_ups.create(session, sign_up)

        return db_entry

    else:
        return {"details": "not authorized"}


@router.post("/{token}")
async def create_user_with_token(
    token: str,
    new_user: UserIn,
    session: Session = Depends(generate_session),
):
    """ Creates a user with a valid sign up token """

    # Validate Token
    db_entry = db.sign_ups.get(session, token, limit=1)
    if not db_entry:
        return {"details": "invalid token"}

    # Create User
    new_user.password = get_password_hash(new_user.password)
    data = db.users.create(session, new_user.dict())

    # DeleteToken
    db.sign_ups.delete(session, token)

    # Respond
    return SnackResponse.success(f"User Created: {new_user.full_name}", data)


@router.delete("/{token}")
async def delete_token(
    token: str,
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Removed a token from the database """
    if current_user.admin:
        db.sign_ups.delete(session, token)
        return SnackResponse.error("Sign Up Token Deleted")
    else:
        return {"details", "not authorized"}
