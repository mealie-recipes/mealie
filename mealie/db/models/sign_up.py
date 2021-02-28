from db.models.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy import Column, Integer, String


class SignUp(SqlAlchemyBase, BaseMixins):
    __tablename__ = "sign_ups"
    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, index=True)
    name = Column(String, index=True)

    def __init__(
        self,
        session,
        token,
        name,
    ) -> None:
        self.token = token
        self.name = name

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "token": self.token,
        }
