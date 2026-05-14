import string
from datetime import datetime
from typing import Annotated, ClassVar, get_origin

from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, synonym
from text_unidecode import unidecode

from ._model_utils.datetime import NaiveDateTime, get_utc_now

# Punctuation characters replaced with spaces during text normalization.
# Mirrors SearchFilter in query_search.py: string.punctuation minus apostrophe and
# double-quote, which are reserved for quoted literal searches.
NORMALIZE_PUNCTUATION = string.punctuation.replace("'", "").replace('"', "")
_NORMALIZE_PUNCTUATION_TABLE = str.maketrans(NORMALIZE_PUNCTUATION, " " * len(NORMALIZE_PUNCTUATION))


class PrivateColumn[T]:
    """
    Drop-in replacement for `Mapped[]` that marks a column as private.
    Private columns cannot be used in query filter expressions.

    Only valid on scalar column fields. Using it on a relationship type (e.g. `list[Model]`)
    will raise a `TypeError` at class definition time.
    """

    def __class_getitem__(cls, item: type) -> type:
        if get_origin(item) is list or item is list:
            raise TypeError(
                f"PrivateColumn cannot be used on relationship fields (got {item!r}). "
                "Annotate the related model's scalar column directly instead."
            )
        return Mapped[Annotated[item, mapped_column(info={"private": True})]]


class SqlAlchemyBase(DeclarativeBase):
    __filter_restricted__: ClassVar[bool] = False
    """When True, the query filter API will block traversal into this model unless explicitly allowed."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(NaiveDateTime, default=get_utc_now, index=True)
    update_at: Mapped[datetime | None] = mapped_column(NaiveDateTime, default=get_utc_now, onupdate=get_utc_now)

    @declared_attr
    def updated_at(cls) -> Mapped[datetime | None]:
        return synonym("update_at")

    @classmethod
    def normalize(cls, val: str) -> str:
        # We cap the length to 255 to prevent indexes from being too long; see:
        # https://www.postgresql.org/docs/current/btree.html
        return unidecode(val).translate(_NORMALIZE_PUNCTUATION_TABLE).lower().strip()[:255]


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
