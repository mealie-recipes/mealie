from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.user import GroupBase, GroupInDB, UpdateGroup, UserInDB
from mealie.services.events import create_group_event
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/groups", tags=["Groups"])


@router.get("", response_model=list[GroupInDB])
async def get_all_groups(
    current_user=Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Returns a list of all groups in the database """

    return db.groups.get_all(session)


@router.get("/self", response_model=GroupInDB)
async def get_current_user_group(
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Returns the Group Data for the Current User """
    current_user: UserInDB

    return db.groups.get(session, current_user.group, "name")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_group(
    background_tasks: BackgroundTasks,
    group_data: GroupBase,
    current_user=Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Creates a Group in the Database """

    try:
        db.groups.create(session, group_data.dict())
        background_tasks.add_task(create_group_event, "Group Created", f"'{group_data.name}' created", session)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@router.put("/{id}")
async def update_group_data(
    id: int,
    group_data: UpdateGroup,
    current_user=Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Updates a User Group """
    db.groups.update(session, id, group_data.dict())


@router.delete("/{id}")
async def delete_user_group(
    background_tasks: BackgroundTasks,
    id: int,
    current_user: UserInDB = Depends(get_current_user),
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
