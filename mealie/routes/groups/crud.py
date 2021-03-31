from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.snackbar import SnackResponse
from mealie.schema.user import GroupBase, GroupInDB, UpdateGroup, UserInDB
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


@router.post("")
async def create_group(
    group_data: GroupBase,
    current_user=Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Creates a Group in the Database """

    try:
        db.groups.create(session, group_data.dict())
        return SnackResponse.success("User Group Created", {"created": True})
    except:
        return SnackResponse.error("User Group Creation Failed")


@router.put("/{id}")
async def update_group_data(
    id: int,
    group_data: UpdateGroup,
    current_user=Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Updates a User Group """
    db.groups.update(session, id, group_data.dict())

    return SnackResponse.success("Group Settings Updated")


@router.delete("/{id}")
async def delete_user_group(
    id: int, current_user=Depends(get_current_user), session: Session = Depends(generate_session)
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
