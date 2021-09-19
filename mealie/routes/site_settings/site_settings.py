from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session

from mealie.core.dependencies import get_current_user
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import AdminAPIRouter
from mealie.schema.admin import SiteSettings
from mealie.schema.user import GroupInDB, PrivateUser
from mealie.utils.post_webhooks import post_webhooks

public_router = APIRouter(prefix="/api/site-settings", tags=["Settings"])
admin_router = AdminAPIRouter(prefix="/api/site-settings", tags=["Settings"])


@public_router.get("")
def get_main_settings(session: Session = Depends(generate_session)):
    """ Returns basic site settings """
    db = get_database(session)

    return db.settings.get(1)


@admin_router.put("")
def update_settings(
    data: SiteSettings,
    session: Session = Depends(generate_session),
):
    """ Returns Site Settings """
    db = get_database(session)
    db.settings.update(1, data.dict())


@admin_router.post("/webhooks/test")
def test_webhooks(
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Run the function to test your webhooks """
    db = get_database(session)
    group_entry: GroupInDB = db.groups.get(current_user.group, "name")

    try:
        post_webhooks(group_entry.id, session)
    except Exception:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
