import uuid
from datetime import datetime

from mealie.db.db_setup import SessionLocal
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declarative_base


def get_uuid_as_hex() -> str:
    """
    Generate a UUID as a hex string.
    :return: UUID as a hex string.
    """
    return uuid.uuid4().hex


@as_declarative()
class Base:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())

    # @declared_attr
    # def __tablename__(cls):
    #     return cls.__name__.lower()


class BaseMixins:
    """
    `self.update` method which directly passing arugments to the `__init__`
    `cls.get_ref` method which will return the object from the database or none. Useful for many-to-many relationships.
    """

    class Config:
        get_attr = "id"

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)

    @classmethod
    def get_ref(cls, match_value: str, match_attr: str = None):
        match_attr = match_attr = cls.Config.get_attr

        if match_value is None:
            return None

        with SessionLocal() as session:
            eff_ref = getattr(cls, match_attr)
            return session.query(cls).filter(eff_ref == match_value).one_or_none()


SqlAlchemyBase = declarative_base(cls=Base, constructor=None)
