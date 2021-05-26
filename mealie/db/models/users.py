from mealie.core.config import settings
from mealie.db.models.group import Group
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm


class LongLiveToken(SqlAlchemyBase, BaseMixins):
    __tablename__ = "long_live_tokens"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    token = Column(String, nullable=False)
    user = orm.relationship("User")

    def __init__(self, session, name, token, parent_id) -> None:
        self.name = name
        self.token = token
        self.user = User.get_ref(session, parent_id)


class User(SqlAlchemyBase, BaseMixins):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, index=True)
    username = Column(
        String,
        index=True,
        unique=True,
    )
    email = Column(String, unique=True, index=True)
    password = Column(String)
    group_id = Column(Integer, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="users")
    admin = Column(Boolean, default=False)
    tokens: list[LongLiveToken] = orm.relationship(
        LongLiveToken, back_populates="user", cascade="all, delete, delete-orphan", single_parent=True
    )

    def __init__(
        self, session, full_name, email, password, group: str = settings.DEFAULT_GROUP, admin=False, **_
    ) -> None:

        group = group or settings.DEFAULT_GROUP
        self.full_name = full_name
        self.email = email
        self.group = Group.get_ref(session, group)
        self.admin = admin
        self.password = password

        if self.username is None:
            self.username = full_name

    def update(self, full_name, email, group, admin, username, session=None, id=None, password=None, *args, **kwargs):
        self.username = username
        self.full_name = full_name
        self.email = email
        self.group = Group.get_ref(session, group)
        self.admin = admin

        if self.username is None:
            self.username = full_name

        if password:
            self.password = password

    def update_password(self, password):
        self.password = password

    @staticmethod
    def get_ref(session, id: str):
        return session.query(User).filter(User.id == id).one()
