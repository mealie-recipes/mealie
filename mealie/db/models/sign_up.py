from sqlalchemy import Boolean, Column, Integer, String

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase


class SignUp(SqlAlchemyBase, BaseMixins):
    __tablename__ = "sign_ups"
    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, index=True)
    name = Column(String, index=True)
    admin = Column(Boolean, default=False)

    def __init__(
        self,
        session,
        token,
        name,
        admin,
    ) -> None:
        self.token = token
        self.name = name
        self.admin = admin
