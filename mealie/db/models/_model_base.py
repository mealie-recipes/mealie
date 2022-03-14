from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import Session


@as_declarative()
class Base:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseMixins:
    """
    `self.update` method which directly passing arugments to the `__init__`
    `cls.get_ref` method which will return the object from the database or none. Useful for many-to-many relationships.
    """

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)

    @classmethod
    def get_ref(cls, match_value: str, match_attr: str = None, session: Session = None):
        match_attr = match_attr or cls.Config.get_attr  # type: ignore

        if match_value is None or session is None:
            return None

        eff_ref = getattr(cls, match_attr)

        return session.query(cls).filter(eff_ref == match_value).one_or_none()


SqlAlchemyBase = declarative_base(cls=Base, constructor=None)
