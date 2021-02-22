from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from models.settings_models import SiteSettings
from sqlalchemy.orm.session import Session
from utils.post_webhooks import post_webhooks
from utils.snackbar import SnackResponse

router = APIRouter(prefix="/api/site-settings", tags=["Settings"])


@router.get("")
def get_main_settings(session: Session = Depends(generate_session)):
    """ Returns basic site settings """

    try:
        data = db.settings.get(session, "main")
    except:
        return
    return data


@router.put("")
def update_settings(data: SiteSettings, session: Session = Depends(generate_session)):
    """ Returns Site Settings """
    db.settings.update(session, "main", data.dict())

    return SnackResponse.success("Settings Updated")


@router.post("/webhooks/test")
def test_webhooks():
    """ Run the function to test your webhooks """

    return post_webhooks()
