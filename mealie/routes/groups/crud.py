from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from routes.deps import manager
from schema.snackbar import SnackResponse
from schema.user import GroupBase, GroupInDB
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/groups", tags=["Groups"])


@router.get("", response_model=list[GroupInDB])
async def get_all_groups(
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Returns a list of all groups in the database """

    return db.groups.get_all(session)


@router.post("")
async def create_group(
    group_data: GroupBase,
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Creates a Group in the Database """

    db.groups.create(session, group_data.dict())

    return


@router.put("/{id}")
async def update_group_data(
    id: int,
    group_data: GroupInDB,
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Updates a User Group """

    return db.groups.update(session, id, group_data.dict())


@router.delete("/{id}")
async def delete_user_group(
    id: int, current_user=Depends(manager), session: Session = Depends(generate_session)
):
    """ Removes a user group from the database """

    if id == 1:
        return SnackResponse.error("Cannot delete default group")

    group: GroupInDB = db.groups.get(session, id)

    if not group:
        return SnackResponse.error("Group not found")

    if not group.users == []:
        return SnackResponse.error("Cannot delete group with users")

    db.groups.delete(session, id)

    return
