from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy import Boolean, Column, DateTime, Integer, String


class EventNotification(SqlAlchemyBase, BaseMixins):
    __tablename__ = "event_notifications"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    notification_url = Column(String)

    # Event Types
    general = Column(Boolean, default=False)
    recipe = Column(Boolean, default=False)
    backup = Column(Boolean, default=False)
    scheduled = Column(Boolean, default=False)
    migration = Column(Boolean, default=False)
    group = Column(Boolean, default=False)
    user = Column(Boolean, default=False)

    def __init__(
        self, name, notification_url, type, general, recipe, backup, scheduled, migration, group, user, *args, **kwargs
    ) -> None:
        self.name = name
        self.notification_url = notification_url
        self.type = type
        self.general = general
        self.recipe = recipe
        self.backup = backup
        self.scheduled = scheduled
        self.migration = migration
        self.group = group
        self.user = user


class Event(SqlAlchemyBase, BaseMixins):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    text = Column(String)
    time_stamp = Column(DateTime)
    category = Column(String)

    def __init__(self, title, text, time_stamp, category, *args, **kwargs) -> None:
        self.title = title
        self.text = text
        self.time_stamp = time_stamp
        self.category = category
