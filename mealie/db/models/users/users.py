from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm

from mealie.core.config import get_app_settings

from .._model_base import BaseMixins, SqlAlchemyBase
from ..group import Group
from .user_to_favorite import users_to_favorites

settings = get_app_settings()


class LongLiveToken(SqlAlchemyBase, BaseMixins):
    __tablename__ = "long_live_tokens"
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
    full_name = Column(String, index=True)
    username = Column(String, index=True, unique=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    admin = Column(Boolean, default=False)
    advanced = Column(Boolean, default=False)

    group_id = Column(Integer, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="users")

    # Group Permissions
    can_manage = Column(Boolean, default=False)
    can_invite = Column(Boolean, default=False)
    can_organize = Column(Boolean, default=False)

    tokens: list[LongLiveToken] = orm.relationship(
        LongLiveToken, back_populates="user", cascade="all, delete, delete-orphan", single_parent=True
    )

    comments: list = orm.relationship(
        "RecipeComment", back_populates="user", cascade="all, delete, delete-orphan", single_parent=True
    )

    password_reset_tokens = orm.relationship(
        "PasswordResetModel", back_populates="user", cascade="all, delete, delete-orphan", single_parent=True
    )

    owned_recipes_id = Column(Integer, ForeignKey("recipes.id"))
    owned_recipes = orm.relationship("RecipeModel", single_parent=True, foreign_keys=[owned_recipes_id])

    favorite_recipes = orm.relationship("RecipeModel", secondary=users_to_favorites, back_populates="favorited_by")

    def __init__(
        self,
        session,
        full_name,
        email,
        password,
        favorite_recipes: list[str] = None,
        group: str = settings.DEFAULT_GROUP,
        advanced=False,
        **kwargs
    ) -> None:
        group = group or settings.DEFAULT_GROUP
        favorite_recipes = favorite_recipes or []
        self.group = Group.get_ref(session, group)

        self.full_name = full_name
        self.email = email
        self.password = password
        self.advanced = advanced

        self.favorite_recipes = []

        if self.username is None:
            self.username = full_name

        self._set_permissions(**kwargs)

    def update(self, full_name, email, group, username, session=None, favorite_recipes=None, advanced=False, **kwargs):
        favorite_recipes = favorite_recipes or []
        self.username = username
        self.full_name = full_name
        self.email = email

        self.group = Group.get_ref(session, group)
        self.advanced = advanced

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
        else:
            self.can_manage = can_manage
            self.can_invite = can_invite
            self.can_organize = can_organize

    @staticmethod
    def get_ref(session, id: str):
        return session.query(User).filter(User.id == id).one()
