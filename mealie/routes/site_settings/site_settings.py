from fastapi import APIRouter, Depends, HTTPException, status
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user, get_admin_user
from mealie.schema.settings import SiteSettings
from mealie.schema.user import GroupInDB, UserInDB
from mealie.utils.post_webhooks import post_webhooks
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/site-settings", tags=["Settings"])


@router.get("")
def get_main_settings(session: Session = Depends(generate_session)):
    """ Returns basic site settings """

    return db.settings.get(session, 1)


@router.put("", dependencies=[Depends(get_admin_user)])
def update_settings(
    data: SiteSettings,
    session: Session = Depends(generate_session),
):
    """ Returns Site Settings """
    db.settings.update(session, 1, data.dict())


@router.post("/webhooks/test", dependencies=[Depends(get_admin_user)])
def test_webhooks(
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Run the function to test your webhooks """
    group_entry: GroupInDB = db.groups.get(session, current_user.group, "name")

    try:
        post_webhooks(group_entry.id, session)
    except Exception:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
