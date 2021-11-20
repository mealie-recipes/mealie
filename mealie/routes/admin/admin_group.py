from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm.session import Session

from mealie.core.dependencies import get_current_user
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import AdminAPIRouter
from mealie.schema.user import GroupBase, GroupInDB, PrivateUser, UpdateGroup
from mealie.services.events import create_group_event

router = AdminAPIRouter(prefix="/groups")


@router.get("", response_model=list[GroupInDB])
async def get_all_groups(session: Session = Depends(generate_session)):
    """Returns a list of all groups in the database"""
    db = get_database(session)

    return db.groups.get_all()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GroupInDB)
async def create_group(
    background_tasks: BackgroundTasks,
    group_data: GroupBase,
    session: Session = Depends(generate_session),
):
    """Creates a Group in the Database"""
    db = get_database(session)

    try:
        new_group = db.groups.create(group_data.dict())
        background_tasks.add_task(create_group_event, "Group Created", f"'{group_data.name}' created", session)
        return new_group
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@router.put("/{id}")
async def update_group_data(id: int, group_data: UpdateGroup, session: Session = Depends(generate_session)):
    """Updates a User Group"""
    db = get_database(session)
    db.groups.update(id, group_data.dict())


@router.delete("/{id}")
async def delete_user_group(
    background_tasks: BackgroundTasks,
    id: int,
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """Removes a user group from the database"""
    db = get_database(session)

    if id == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DEFAULT_GROUP")

    group: GroupInDB = db.groups.get(id)

    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GROUP_NOT_FOUND")

    if group.users != []:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GROUP_WITH_USERS")

    background_tasks.add_task(
        create_group_event, "Group Deleted", f"'{group.name}' deleted by {current_user.full_name}", session
    )

    db.groups.delete(id)
