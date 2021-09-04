from sqlalchemy import Boolean, Column, Integer, String

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from ._model_utils import auto_init


class SignUp(SqlAlchemyBase, BaseMixins):
    __tablename__ = "sign_ups"
    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, index=True)
    name = Column(String, index=True)
    admin = Column(Boolean, default=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
