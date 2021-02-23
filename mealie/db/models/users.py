from db.models.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy import Boolean, Column, Integer, String


class User(SqlAlchemyBase, BaseMixins):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean(), default=True)
    family = Column(String)
    admin = Column(Boolean(), default=False)

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
