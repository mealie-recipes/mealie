from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from text_unidecode import unidecode

from ._model_utils.helpers import get_utc_now


class SqlAlchemyBase(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=get_utc_now, index=True)
    update_at: Mapped[datetime | None] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    @classmethod
    def normalize(cls, val: str) -> str:
        return unidecode(val).lower().strip()


class BaseMixins:
    """
    `self.update` method which directly passing arguments to the `__init__`
    """

    def update(self, *args, **kwargs):
        self.__init__(*args, **kwargs)

        # sqlalchemy doesn't like this method to remove all instances of a 1:many relationship,
        # so we explicitly check for that here
        for k, v in kwargs.items():
            if hasattr(self, k) and v == []:
                setattr(self, k, v)
