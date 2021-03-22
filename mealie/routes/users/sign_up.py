import uuid

from mealie.core.security import get_password_hash
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from fastapi import APIRouter, Depends
from mealie.routes.deps import get_current_user
from mealie.schema.sign_up import SignUpIn, SignUpOut, SignUpToken
from mealie.schema.snackbar import SnackResponse
from mealie.schema.user import UserIn, UserInDB
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/users/sign-ups", tags=["User Signup"])


@router.get("", response_model=list[SignUpOut])
async def get_all_open_sign_ups(
    current_user=Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Returns a list of open sign up links """

    all_sign_ups = db.sign_ups.get_all(session)

    return all_sign_ups


@router.post("", response_model=SignUpToken)
async def create_user_sign_up_key(
    key_data: SignUpIn,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Generates a Random Token that a new user can sign up with """

    if current_user.admin:
        sign_up = {
            "token": str(uuid.uuid1().hex),
            "name": key_data.name,
            "admin": key_data.admin,
        }
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
    db_entry: SignUpOut = db.sign_ups.get(session, token, limit=1)
    if not db_entry:
        return SnackResponse.error("Invalid Token")

    # Create User
    new_user.admin = db_entry.admin
    new_user.password = get_password_hash(new_user.password)
    data = db.users.create(session, new_user.dict())

    # DeleteToken
    db.sign_ups.delete(session, token)

    # Respond
    return SnackResponse.success(f"User Created: {new_user.full_name}", data)


@router.delete("/{token}")
async def delete_token(
    token: str,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Removed a token from the database """
    if current_user.admin:
        db.sign_ups.delete(session, token)
        return SnackResponse.error("Sign Up Token Deleted")
    else:
        return {"details", "not authorized"}
