from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase


class SqlAlchemyBase(DeclarativeBase):
    __allow_unmapped__ = True
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseMixins:
    """
    `self.update` method which directly passing arguments to the `__init__`
    """

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)
