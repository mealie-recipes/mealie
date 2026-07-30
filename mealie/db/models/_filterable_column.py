from typing import TYPE_CHECKING, Annotated

from sqlalchemy.orm import Mapped, mapped_column


class _FilterableColumn[T]:
    """
    Drop-in replacement for `Mapped[]` that marks a column as filterable.
    Filterable columns can be used in query filter expressions.

    Only valid on scalar column fields. Using it on a relationship type (e.g. `list[Model]`).
    """

    def __class_getitem__(cls, item: type) -> type:
        return Mapped[Annotated[item, mapped_column(info={"filterable": True})]]


# SQLAlchemy doesn't play nice with mypy when overriding Mapped, so
# we use this awkward workaround to make mypy happy
if TYPE_CHECKING:
    FilterableColumn = Mapped
else:
    FilterableColumn = _FilterableColumn
