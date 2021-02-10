from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from services.settings_services import SiteSettings
from sqlalchemy.orm.session import Session
from utils.post_webhooks import post_webhooks
from utils.snackbar import SnackResponse

router = APIRouter(prefix="/api/site-settings", tags=["Settings"])


@router.get("")
def get_main_settings(db: Session = Depends(generate_session)):
    """ Returns basic site settings """

    return SiteSettings.get_site_settings(db)


@router.post("/webhooks/test")
def test_webhooks():
    """ Run the function to test your webhooks """

    return post_webhooks()


@router.put("")
def update_settings(data: SiteSettings, db: Session = Depends(generate_session)):
    """ Returns Site Settings """
    data.update(db)

    return SnackResponse.success("Settings Updated")
