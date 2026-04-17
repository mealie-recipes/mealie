from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from .users import User


class UserMLPreferences(SqlAlchemyBase, BaseMixins):
    __tablename__ = "user_ml_preferences"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    user_id: Mapped[GUID] = mapped_column(
        GUID,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    user: Mapped[Optional["User"]] = orm.relationship("User", back_populates="ml_preferences")

    taste_vector: Mapped[list[float] | None] = mapped_column(sa.JSON, nullable=True)
    onboarding_tags: Mapped[list[str] | None] = mapped_column(sa.JSON, nullable=True)
    rating_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
