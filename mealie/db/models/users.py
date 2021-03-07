from core.config import DEFAULT_GROUP
from db.models.group import Group
from db.models.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm


class User(SqlAlchemyBase, BaseMixins):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    group_id = Column(String, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="users")
    admin = Column(Boolean, default=False)

    def __init__(
        self,
        session,
        full_name,
        email,
        password,
        group: str = DEFAULT_GROUP,
        admin=False,
    ) -> None:

        group = group if group else DEFAULT_GROUP
        self.full_name = full_name
        self.email = email
        self.group = Group.create_if_not_exist(session, group)
        self.admin = admin
        self.password = password

    def update(self, full_name, email, group, admin, session=None):
        self.full_name = full_name
        self.email = email
        self.group = Group.create_if_not_exist(session, group)
        self.admin = admin

    def update_password(self, password):
        self.password = password
