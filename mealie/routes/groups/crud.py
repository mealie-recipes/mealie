from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm.session import Session

from mealie.core.dependencies import get_current_user
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.routers import AdminAPIRouter, UserAPIRouter
from mealie.schema.user import GroupBase, GroupInDB, PrivateUser, UpdateGroup
from mealie.services.events import create_group_event

admin_router = AdminAPIRouter(prefix="/groups", tags=["Groups: CRUD"])
user_router = UserAPIRouter(prefix="/groups", tags=["Groups: CRUD"])


@admin_router.get("", response_model=list[GroupInDB])
async def get_all_groups(session: Session = Depends(generate_session)):
    """ Returns a list of all groups in the database """

    return db.groups.get_all(session)


@admin_router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupInDB)
async def create_group(
    background_tasks: BackgroundTasks,
    group_data: GroupBase,
    session: Session = Depends(generate_session),
):
    """ Creates a Group in the Database """

    try:
        new_group = db.groups.create(session, group_data.dict())
        background_tasks.add_task(create_group_event, "Group Created", f"'{group_data.name}' created", session)
        return new_group
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@admin_router.put("/{id}")
async def update_group_data(id: int, group_data: UpdateGroup, session: Session = Depends(generate_session)):
    """ Updates a User Group """
    db.groups.update(session, id, group_data.dict())


@admin_router.delete("/{id}")
async def delete_user_group(
    background_tasks: BackgroundTasks,
    id: int,
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Removes a user group from the database """

    if id == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DEFAULT_GROUP")

    group: GroupInDB = db.groups.get(session, id)

    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GROUP_NOT_FOUND")

    if group.users != []:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GROUP_WITH_USERS")

    background_tasks.add_task(
        create_group_event, "Group Deleted", f"'{group.name}' deleted by {current_user.full_name}", session
    )

    db.groups.delete(session, id)
