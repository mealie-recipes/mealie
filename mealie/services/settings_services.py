from db.database import db
from db.db_setup import create_session, sql_exists
from models.settings_models import SiteSettings, Webhooks


def default_settings_init():
    session = create_session()
    try:
        document = db.settings.get(session, "main")
    except:
        webhooks = Webhooks()
        default_entry = SiteSettings(name="main", webhooks=webhooks)
        document = db.settings.create(session, default_entry.dict(), webhooks.dict())

    session.close()


if not sql_exists:
    default_settings_init()
