from typing import TYPE_CHECKING, Annotated, get_origin

from sqlalchemy.orm import Mapped, mapped_column


class _FilterableColumn[T]:
    """
    Drop-in replacement for `Mapped[]` that marks a column as filterable.
    Filterable columns can be used in query filter expressions.

    Only valid on scalar column fields. Using it on a relationship type (e.g. `list[Model]`)
    will raise a `TypeError` at class definition time.
    """

    def __class_getitem__(cls, item: type) -> type:
        if get_origin(item) is list or item is list:
            raise TypeError(
                f"FilterableColumn cannot be used on relationship fields (got {item!r}). "
                "Annotate the related model's scalar column directly instead."
            )
        return Mapped[Annotated[item, mapped_column(info={"filterable": True})]]


# SQLAlchemy doesn't play nice with mypy when overriding Mapped, so
# we use this awkward workaround to make mypy happy
if TYPE_CHECKING:
    FilterableColumn = Mapped
else:
    FilterableColumn = _FilterableColumn
