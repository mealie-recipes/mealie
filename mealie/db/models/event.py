from sqlalchemy import Boolean, Column, DateTime, Integer, String

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from ._model_utils import auto_init


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

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class Event(SqlAlchemyBase, BaseMixins):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    text = Column(String)
    time_stamp = Column(DateTime)
    category = Column(String)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
