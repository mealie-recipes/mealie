from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from text_unidecode import unidecode


def _get_now_utc():
    return datetime.now(timezone.utc)


class SqlAlchemyBase(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=_get_now_utc, index=True)
    update_at: Mapped[datetime | None] = mapped_column(DateTime, default=_get_now_utc, onupdate=_get_now_utc)

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
