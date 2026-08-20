from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint, orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, FilterableColumn, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from .users import User


class UserIpBlocklist(SqlAlchemyBase, BaseMixins):
    __tablename__ = "user_ip_blocklist"
    __table_args__ = (UniqueConstraint("user_id", "ip_address", name="user_ip_blocklist_user_id_ip_address_key"),)

    # Use UUID id so it matches your LoginHistoryOut schema (UUID4)
    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # Keep nullable=True so failed login with unknown username can also be stored
    user_id: FilterableColumn[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    reason: FilterableColumn[str | None] = mapped_column(String, nullable=True)
    ip_address: FilterableColumn[str] = mapped_column(String, nullable=False, index=True)
    created_by_user_id: FilterableColumn[GUID | None] = mapped_column(GUID, ForeignKey("users.id"), nullable=True)
    user: Mapped[Optional["User"]] = orm.relationship(
        "User", back_populates="ip_blocked_entries", foreign_keys=[user_id]
    )

    @auto_init()
    def __init__(self, **_) -> None:
        pass
