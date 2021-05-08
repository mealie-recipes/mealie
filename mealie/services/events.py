import apprise
from mealie.db.database import db
from mealie.db.db_setup import create_session
from mealie.schema.events import Event, EventCategory
from sqlalchemy.orm.session import Session


def post_notifications(event: Event, notification_urls=list[str]):
    asset = apprise.AppriseAsset(async_mode=False)
    apobj = apprise.Apprise(asset=asset)

    for dest in notification_urls:
        apobj.add(dest)

    apobj.notify(
        body=event.text,
        title=event.title,
    )


def save_event(title, text, category, session: Session):
    event = Event(title=title, text=text, category=category)
    session = session or create_session()
    db.events.create(session, event.dict())

    notification_objects = db.event_notifications.get(session=session, match_value=True, match_key=category, limit=9999)
    notification_urls = [x.notification_url for x in notification_objects]
    post_notifications(event, notification_urls)


def create_general_event(title, text, session=None):
    category = EventCategory.general
    save_event(title=title, text=text, category=category, session=session)


def create_recipe_event(title, text, session=None):
    category = EventCategory.recipe

    save_event(title=title, text=text, category=category, session=session)


def create_backup_event(title, text, session=None):
    category = EventCategory.backup
    save_event(title=title, text=text, category=category, session=session)


def create_scheduled_event(title, text, session=None):
    category = EventCategory.scheduled
    save_event(title=title, text=text, category=category, session=session)


def create_migration_event(title, text, session=None):
    category = EventCategory.migration
    save_event(title=title, text=text, category=category, session=session)


def create_group_event(title, text, session=None):
    category = EventCategory.group
    save_event(title=title, text=text, category=category, session=session)


def create_user_event(title, text, session=None):
    category = EventCategory.user
    save_event(title=title, text=text, category=category, session=session)
