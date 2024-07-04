from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from .users import User


class PasswordResetModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "password_reset_tokens"

    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = orm.relationship("User", back_populates="password_reset_tokens", uselist=False)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    def __init__(self, user_id, token, **_):
        self.user_id = user_id
        self.token = token
