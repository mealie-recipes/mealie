from sqlalchemy import Boolean, Column, ForeignKey, String, orm

from mealie.core.config import get_app_settings
from mealie.db.models._model_utils.guid import GUID

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init
from .user_to_favorite import users_to_favorites


class LongLiveToken(SqlAlchemyBase, BaseMixins):
    __tablename__ = "long_live_tokens"
    name = Column(String, nullable=False)
    token = Column(String, nullable=False)

    user_id = Column(GUID, ForeignKey("users.id"))
    user = orm.relationship("User")

    def __init__(self, name, token, user_id, **_) -> None:
        self.name = name
        self.token = token
        self.user_id = user_id


class User(SqlAlchemyBase, BaseMixins):
    __tablename__ = "users"
    id = Column(GUID, primary_key=True, default=GUID.generate)
    full_name = Column(String, index=True)
    username = Column(String, index=True, unique=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    admin = Column(Boolean, default=False)
    advanced = Column(Boolean, default=False)

    group_id = Column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group = orm.relationship("Group", back_populates="users")

    cache_key = Column(String, default="1234")

    # Group Permissions
    can_manage = Column(Boolean, default=False)
    can_invite = Column(Boolean, default=False)
    can_organize = Column(Boolean, default=False)

    sp_args = {
        "back_populates": "user",
        "cascade": "all, delete, delete-orphan",
        "single_parent": True,
    }

    tokens = orm.relationship(LongLiveToken, **sp_args)
    comments = orm.relationship("RecipeComment", **sp_args)
    password_reset_tokens = orm.relationship("PasswordResetModel", **sp_args)

    owned_recipes_id = Column(GUID, ForeignKey("recipes.id"))
    owned_recipes = orm.relationship("RecipeModel", single_parent=True, foreign_keys=[owned_recipes_id])

    favorite_recipes = orm.relationship("RecipeModel", secondary=users_to_favorites, back_populates="favorited_by")

    class Config:
        exclude = {
            "password",
            "admin",
            "can_manage",
            "can_invite",
            "can_organize",
            "group",
        }

    @auto_init()
    def __init__(self, session, full_name, password, group: str = None, **kwargs) -> None:
        if group is None:
            settings = get_app_settings()
            group = settings.DEFAULT_GROUP

        from mealie.db.models.group import Group

        self.group = Group.get_ref(session, group)

        self.favorite_recipes = []

        self.password = password

        if self.username is None:
            self.username = full_name

        self._set_permissions(**kwargs)

    @auto_init()
    def update(self, full_name, email, group, username, session=None, **kwargs):
        self.username = username
        self.full_name = full_name
        self.email = email

        from mealie.db.models.group import Group

        self.group = Group.get_ref(session, group)

        if self.username is None:
            self.username = full_name

        self._set_permissions(**kwargs)

    def update_password(self, password):
        self.password = password

    def _set_permissions(self, admin, can_manage=False, can_invite=False, can_organize=False, **_):
        """Set user permissions based on the admin flag and the passed in kwargs

        Args:
            admin (bool):
            can_manage (bool):
            can_invite (bool):
            can_organize (bool):
        """
        self.admin = admin
        if self.admin:
            self.can_manage = True
            self.can_invite = True
            self.can_organize = True
            self.advanced = True
        else:
            self.can_manage = can_manage
            self.can_invite = can_invite
            self.can_organize = can_organize

    @staticmethod  # TODO: Remove This
    def get_ref(session, id: str):  # type: ignore
        return session.query(User).filter(User.id == id).one()
