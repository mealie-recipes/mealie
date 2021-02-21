from db.sql.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy import Boolean, Column, Integer, String


class User(SqlAlchemyBase, BaseMixins):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean(), default=True)
    family = Column(String)
    is_superuser = Column(Boolean(), default=False)

    def __init__(
        self,
        session,
        full_name,
        email,
        password,
        family="public",
        is_superuser=False,
    ) -> None:
        self.full_name = full_name
        self.email = email
        self.family = family
        self.is_superuser = is_superuser
        self.password = password

    def dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "is_superuser": self.is_superuser,
            "family": self.family,
            "password": self.password,
        }

    def update(self, full_name, email, family, password, session=None):
        self.full_name = full_name
        self.email = email
        self.family = family
        self.password = password