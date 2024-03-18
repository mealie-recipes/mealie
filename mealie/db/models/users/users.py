import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import ConfigDict
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from mealie.core.config import get_app_settings
from mealie.db.models._model_utils.guid import GUID

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init
from .user_to_favorite import users_to_favorites

if TYPE_CHECKING:
    from ..group import Group
    from ..group.mealplan import GroupMealPlan
    from ..group.shopping_list import ShoppingList
    from ..recipe import RecipeComment, RecipeModel, RecipeTimelineEvent
    from .password_reset import PasswordResetModel


class LongLiveToken(SqlAlchemyBase, BaseMixins):
    __tablename__ = "long_live_tokens"
    name: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(String, nullable=False, index=True)

    user_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("users.id"), index=True)
    user: Mapped[Optional["User"]] = orm.relationship("User")

    def __init__(self, name, token, user_id, **_) -> None:
        self.name = name
        self.token = token
        self.user_id = user_id


class AuthMethod(enum.Enum):
    MEALIE = "Mealie"
    LDAP = "LDAP"
    OIDC = "OIDC"


class User(SqlAlchemyBase, BaseMixins):
    __tablename__ = "users"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    full_name: Mapped[str | None] = mapped_column(String, index=True)
    username: Mapped[str | None] = mapped_column(String, index=True, unique=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    password: Mapped[str | None] = mapped_column(String)
    auth_method: Mapped[Enum[AuthMethod]] = mapped_column(Enum(AuthMethod), default=AuthMethod.MEALIE)
    admin: Mapped[bool | None] = mapped_column(Boolean, default=False)
    advanced: Mapped[bool | None] = mapped_column(Boolean, default=False)

    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="users")

    cache_key: Mapped[str | None] = mapped_column(String, default="1234")
    login_attemps: Mapped[int | None] = mapped_column(Integer, default=0)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    # Group Permissions
    can_manage: Mapped[bool | None] = mapped_column(Boolean, default=False)
    can_invite: Mapped[bool | None] = mapped_column(Boolean, default=False)
    can_organize: Mapped[bool | None] = mapped_column(Boolean, default=False)

    sp_args = {
        "back_populates": "user",
        "cascade": "all, delete, delete-orphan",
        "single_parent": True,
    }

    tokens: Mapped[list[LongLiveToken]] = orm.relationship(LongLiveToken, **sp_args)
    comments: Mapped[list["RecipeComment"]] = orm.relationship("RecipeComment", **sp_args)
    recipe_timeline_events: Mapped[list["RecipeTimelineEvent"]] = orm.relationship("RecipeTimelineEvent", **sp_args)
    password_reset_tokens: Mapped[list["PasswordResetModel"]] = orm.relationship("PasswordResetModel", **sp_args)

    owned_recipes_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"))
    owned_recipes: Mapped[Optional["RecipeModel"]] = orm.relationship(
        "RecipeModel", single_parent=True, foreign_keys=[owned_recipes_id]
    )
    mealplans: Mapped[Optional["GroupMealPlan"]] = orm.relationship(
        "GroupMealPlan", order_by="GroupMealPlan.date", **sp_args
    )
    shopping_lists: Mapped[Optional["ShoppingList"]] = orm.relationship("ShoppingList", **sp_args)
    favorite_recipes: Mapped[list["RecipeModel"]] = orm.relationship(
        "RecipeModel", secondary=users_to_favorites, back_populates="favorited_by"
    )
    model_config = ConfigDict(
        exclude={
            "password",
            "admin",
            "can_manage",
            "can_invite",
            "can_organize",
            "group",
        }
    )

    @hybrid_property
    def group_slug(self) -> str:
        return self.group.slug

    @auto_init()
    def __init__(self, session, full_name, password, group: str | None = None, **kwargs) -> None:
        if group is None:
            settings = get_app_settings()
            group = settings.DEFAULT_GROUP

        from mealie.db.models.group import Group

        self.group = Group.get_by_name(session, group)

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

        self.group = Group.get_by_name(session, group)

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
