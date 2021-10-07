from sqlalchemy import Column, ForeignKey, Integer, String, orm

from .._model_base import BaseMixins, SqlAlchemyBase


class PasswordResetModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "password_reset_tokens"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = orm.relationship("User", back_populates="password_reset_tokens", uselist=False)
    token = Column(String(64), unique=True, nullable=False)

    def __init__(self, user_id, token, **_):
        self.user_id = user_id
        self.token = token
