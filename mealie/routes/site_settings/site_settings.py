from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.settings import SiteSettings
from mealie.schema.snackbar import SnackResponse
from mealie.schema.user import GroupInDB, UserInDB
from mealie.utils.post_webhooks import post_webhooks
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/site-settings", tags=["Settings"])


@router.get("")
def get_main_settings(session: Session = Depends(generate_session)):
    """ Returns basic site settings """

    return db.settings.get(session, 1)


@router.put("")
def update_settings(
    data: SiteSettings,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Returns Site Settings """
    db.settings.update(session, 1, data.dict())

    return SnackResponse.success("Settings Updated")


@router.post("/webhooks/test")
def test_webhooks(
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Run the function to test your webhooks """
    group_entry: GroupInDB = db.groups.get(session, current_user.group, "name")

    return post_webhooks(group_entry.id, session)
