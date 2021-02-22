from core.security import get_password_hash
from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from models.user_models import CreateUser, UserResponse
from routes.deps import manager
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    new_user: CreateUser,
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Returns a list of all user in the Database """

    new_user.password = get_password_hash(new_user.password)

    data = db.users.create(session, new_user.dict())
    return data


@router.get("", response_model=list[UserResponse])
async def get_all_users(
    current_user=Depends(manager), session: Session = Depends(generate_session)
):

    if current_user.get("is_superuser"):
        return db.users.get_all(session)
    else:
        return {"details": "user not authorized"}


@router.get("/{id}", response_model=UserResponse)
async def get_user_by_id(
    id: int, current_user=Depends(manager), session: Session = Depends(generate_session)
):
    return db.users.get(session, id)


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id: int,
    new_data: CreateUser,
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):
    current_user_id = current_user.get("id")
    new_data.password = get_password_hash(new_data.password)
    is_superuser = current_user.get("is_superuser")
    if current_user_id == id or is_superuser:
        return db.users.update(session, id, new_data.dict())
    return


@router.delete("/{id}")
async def delete_user(
    id: int,
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Removes a user from the database. Must be the current user or a super user"""

    current_user_id = current_user.get("id")
    is_superuser = current_user.get("is_superuser")

    if current_user_id == id or is_superuser:
        return db.users.delete(session, id)
