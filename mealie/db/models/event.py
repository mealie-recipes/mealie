from sqlalchemy import Column, DateTime, Integer, String

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from ._model_utils import auto_init


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
