from core.security import get_password_hash
from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from routes.deps import manager
from schema.user import UserBase, UserIn, UserInDB, UserOut
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    new_user: UserIn,
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Returns a list of all user in the Database """

    new_user.password = get_password_hash(new_user.password)

    data = db.users.create(session, new_user.dict())
    return data


@router.get("", response_model=list[UserOut])
async def get_all_users(
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):

    if current_user.admin:
        return db.users.get_all(session)
    else:
        return {"details": "user not authorized"}


@router.get("/{id}", response_model=UserOut)
async def get_user_by_id(
    id: int,
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    return db.users.get(session, id)


@router.put("/{id}", response_model=UserOut)
async def update_user(
    id: int,
    new_data: UserBase,
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):

    if current_user.id == id or current_user.admin:
        return db.users.update(session, id, new_data.dict())
    return


@router.delete("/{id}")
async def delete_user(
    id: int,
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Removes a user from the database. Must be the current user or a super user"""

    if current_user.id == id or current_user.admin:
        return db.users.delete(session, id)
