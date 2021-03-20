from mealie.db.database import db
from mealie.db.db_setup import generate_session
from fastapi import APIRouter, Depends
from mealie.schema.settings import SiteSettings
from mealie.schema.snackbar import SnackResponse
from mealie.schema.user import GroupInDB, UserInDB
from sqlalchemy.orm.session import Session
from mealie.utils.post_webhooks import post_webhooks

from mealie.routes.deps import manager

router = APIRouter(prefix="/api/site-settings", tags=["Settings"])


@router.get("")
def get_main_settings(session: Session = Depends(generate_session)):
    """ Returns basic site settings """

    data = db.settings.get(session, 1)

    return data


@router.put("")
def update_settings(data: SiteSettings, session: Session = Depends(generate_session)):
    """ Returns Site Settings """
    db.settings.update(session, 1, data.dict())

    return SnackResponse.success("Settings Updated")


@router.post("/webhooks/test")
def test_webhooks(
    current_user: UserInDB = Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Run the function to test your webhooks """
    group_entry: GroupInDB = db.groups.get(session, current_user.group, "name")

    return post_webhooks(group_entry.id, session)
