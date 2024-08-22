from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import guid
from .._model_utils.auto_init import auto_init

if TYPE_CHECKING:
    from ..group import Group
    from .household import Household


class GroupInviteToken(SqlAlchemyBase, BaseMixins):
    __tablename__ = "invite_tokens"
    token: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True)
    uses_left: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    group_id: Mapped[guid.GUID | None] = mapped_column(guid.GUID, ForeignKey("groups.id"), index=True)
    group: Mapped[Optional["Group"]] = orm.relationship("Group", back_populates="invite_tokens")
    household_id: Mapped[guid.GUID | None] = mapped_column(guid.GUID, ForeignKey("households.id"), index=True)
    household: Mapped[Optional["Household"]] = orm.relationship("Household", back_populates="invite_tokens")

    @auto_init()
    def __init__(self, **_):
        pass
