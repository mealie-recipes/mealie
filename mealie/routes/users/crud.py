from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm.session import Session

from mealie.core import security
from mealie.core.dependencies import get_current_user
from mealie.core.security import hash_password
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.routers import AdminAPIRouter, UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.user import PrivateUser, UserBase, UserIn, UserOut
from mealie.services.events import create_user_event

user_router = UserAPIRouter(prefix="")
admin_router = AdminAPIRouter(prefix="")


@admin_router.get("", response_model=list[UserOut])
async def get_all_users(session: Session = Depends(generate_session)):
    return db.users.get_all(session)


@admin_router.post("", response_model=UserOut, status_code=201)
async def create_user(
    background_tasks: BackgroundTasks,
    new_user: UserIn,
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):

    new_user.password = hash_password(new_user.password)
    background_tasks.add_task(
        create_user_event, "User Created", f"Created by {current_user.full_name}", session=session
    )

    return db.users.create(session, new_user.dict())


@admin_router.get("/{id}", response_model=UserOut)
async def get_user(id: int, session: Session = Depends(generate_session)):
    return db.users.get(session, id)


@admin_router.delete("/{id}")
def delete_user(
    background_tasks: BackgroundTasks,
    id: int,
    session: Session = Depends(generate_session),
    current_user: PrivateUser = Depends(get_current_user),
):
    """ Removes a user from the database. Must be the current user or a super user"""

    assert_user_change_allowed(id, current_user)

    if id == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="SUPER_USER")

    try:
        db.users.delete(session, id)
        background_tasks.add_task(create_user_event, "User Deleted", f"User ID: {id}", session=session)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@user_router.get("/self", response_model=UserOut)
async def get_logged_in_user(
    current_user: PrivateUser = Depends(get_current_user),
):
    return current_user.dict()


@user_router.put("/{id}")
async def update_user(
    id: int,
    new_data: UserBase,
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):

    assert_user_change_allowed(id, current_user)

    if not current_user.admin and (new_data.admin or current_user.group != new_data.group):
        # prevent a regular user from doing admin tasks on themself
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    if current_user.id == id and current_user.admin and not new_data.admin:
        # prevent an admin from demoting themself
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    db.users.update(session, id, new_data.dict())
    if current_user.id == id:
        access_token = security.create_access_token(data=dict(sub=new_data.email))
        return {"access_token": access_token, "token_type": "bearer"}
