from mealie.db.database import db
from mealie.db.db_setup import create_session
from mealie.schema.events import Event, EventCategory
from mealie.services.event_notifications import post_notifications
from sqlalchemy.orm.session import Session


def save_event(title, text, category, session: Session):
    event = Event(title=title, text=text, category=category)
    session = session or create_session()
    db.events.create(session, event.dict())

    notification_objects = db.event_notifications.get(session=session, match_value=True, match_key=category, limit=9999)
    post_notifications(event, notification_objects)


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
