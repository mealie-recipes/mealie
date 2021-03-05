from db.models.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy import Boolean, Column, Integer, String


class Group(SqlAlchemyBase, BaseMixins):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    slug = Column(String, unique=True, index=True)

    def __init__(
        self,
        session,
        full_name,
        email,
        password,
        family="public",
        admin=False,
    ) -> None:
        self.full_name = full_name
        self.email = email
        self.family = family
        self.admin = admin
        self.password = password

    def dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "admin": self.admin,
            "family": self.family,
            "password": self.password,
        }

    def update(self, full_name, email, family, admin, session=None):
        self.full_name = full_name
        self.email = email
        self.family = family
        self.admin = admin

