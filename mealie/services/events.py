from sqlalchemy.orm.session import Session

from mealie.db.db_setup import create_session
from mealie.repos.all_repositories import get_repositories
from mealie.schema.events import Event, EventCategory


def save_event(title, text, category, session: Session):
    event = Event(title=title, text=text, category=category)
    session = session or create_session()
    db = get_repositories(session)
    db.events.create(event.dict())


def create_general_event(title, text, session=None):
    category = EventCategory.general
    save_event(title=title, text=text, category=category, session=session)


def create_recipe_event(title, text, session=None, attachment=None):  # noqa
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
