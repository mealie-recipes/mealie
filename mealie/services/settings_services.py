from db.database import db
from db.db_setup import create_session, sql_exists
from models.settings_models import SiteSettings, Webhooks
from sqlalchemy.orm.session import Session


def default_settings_init(session: Session = None):
    if session == None:
        session = create_session()
    try:
        webhooks = Webhooks()
        default_entry = SiteSettings(name="main", webhooks=webhooks)
        document = db.settings.create(session, default_entry.dict(), webhooks.dict())
    except:
        pass

