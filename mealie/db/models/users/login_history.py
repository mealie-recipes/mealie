from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, FilterableColumn, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID
from .users import AuthMethod

if TYPE_CHECKING:
    from .users import User


class UserLoginHistory(SqlAlchemyBase, BaseMixins):
    __tablename__ = "user_login_history"

    # Use UUID id so it matches your LoginHistoryOut schema (UUID4)
    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    username: FilterableColumn[str | None] = mapped_column(String, nullable=True, index=True)
    # Keep nullable=True so failed login with unknown username can also be stored
    user_id: FilterableColumn[GUID | None] = mapped_column(GUID, ForeignKey("users.id"), nullable=True, index=True)
    user: Mapped[Optional["User"]] = orm.relationship("User", back_populates="login_history_entries")

    # Multi-tenant context comes from user when user_id exists
    group_id: AssociationProxy[GUID] = association_proxy("user", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")

    auth_method: FilterableColumn[AuthMethod | None] = mapped_column(Enum(AuthMethod), nullable=True)
    success: FilterableColumn[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    reason: FilterableColumn[str | None] = mapped_column(String, nullable=True)
    ip_address: FilterableColumn[str | None] = mapped_column(String, nullable=True)
    user_agent: FilterableColumn[str | None] = mapped_column(String, nullable=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
