import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import ConfigDict
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, orm, select
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, Session, mapped_column

from mealie.core.config import get_app_settings
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.datetime import NaiveDateTime
from mealie.db.models._model_utils.guid import GUID

from .._model_base import BaseMixins, SqlAlchemyBase
from .user_to_recipe import UserToRecipe

if TYPE_CHECKING:
    from ..group import Group
    from ..household import Household
    from ..household.mealplan import GroupMealPlan
    from ..household.shopping_list import ShoppingList
    from ..recipe import RecipeComment, RecipeModel, RecipeTimelineEvent
    from .password_reset import PasswordResetModel


class LongLiveToken(SqlAlchemyBase, BaseMixins):
    __tablename__ = "long_live_tokens"
    name: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(String, nullable=False, index=True)

    user_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("users.id"), index=True)
    user: Mapped[Optional["User"]] = orm.relationship("User")

    group_id: AssociationProxy[GUID] = association_proxy("user", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")

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
    household_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("households.id"), nullable=True, index=True)
    household: Mapped["Household"] = orm.relationship("Household", back_populates="users")

    cache_key: Mapped[str | None] = mapped_column(String, default="1234")
    login_attemps: Mapped[int | None] = mapped_column(Integer, default=0)
    locked_at: Mapped[datetime | None] = mapped_column(NaiveDateTime, default=None)

    # Group Permissions
    can_manage_household: Mapped[bool | None] = mapped_column(Boolean, default=False)
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
    rated_recipes: Mapped[list["RecipeModel"]] = orm.relationship(
        "RecipeModel",
        secondary=UserToRecipe.__tablename__,
        back_populates="rated_by",
        overlaps="recipe,favorited_by,favorited_recipes",
    )
    favorite_recipes: Mapped[list["RecipeModel"]] = orm.relationship(
        "RecipeModel",
        secondary=UserToRecipe.__tablename__,
        primaryjoin="and_(User.id==UserToRecipe.user_id, UserToRecipe.is_favorite==True)",
        back_populates="favorited_by",
        overlaps="recipe,rated_by,rated_recipes",
    )
    model_config = ConfigDict(
        exclude={
            "password",
            "admin",
            "can_manage_household",
            "can_manage",
            "can_invite",
            "can_organize",
            "group",
            "household",
        }
    )

    @hybrid_property
    def group_slug(self) -> str:
        return self.group.slug

    @hybrid_property
    def household_slug(self) -> str:
        return self.household.slug

    @auto_init()
    def __init__(
        self, session: Session, full_name, password, group: str | None = None, household: str | None = None, **kwargs
    ) -> None:
        if group is None or household is None:
            settings = get_app_settings()
            group = group or settings.DEFAULT_GROUP
            household = household or settings.DEFAULT_HOUSEHOLD

        from mealie.db.models.group import Group
        from mealie.db.models.household import Household

        self.group = session.execute(select(Group).filter(Group.name == group)).scalars().one_or_none()
        if self.group:
            self.household = (
                session.execute(
                    select(Household).filter(Household.name == household, Household.group_id == self.group.id)
                )
                .scalars()
                .one_or_none()
            )
        else:
            self.household = None

        if self.group is None:
            raise ValueError(f"Group {group} does not exist; cannot create user")
        if self.household is None:
            raise ValueError(
                f'Household "{household}" does not exist on group '
                f'"{self.group.name}" ({self.group.id}); cannot create user'
            )

        self.rated_recipes = []

        self.password = password

        if self.username is None:
            self.username = full_name

        self._set_permissions(**kwargs)

    @auto_init()
    def update(self, session: Session, full_name, email, group, household, username, **kwargs):
        self.username = username
        self.full_name = full_name
        self.email = email

        from mealie.db.models.group import Group
        from mealie.db.models.household import Household

        self.group = session.execute(select(Group).filter(Group.name == group)).scalars().one_or_none()
        if self.group:
            self.household = (
                session.execute(
                    select(Household).filter(Household.name == household, Household.group_id == self.group.id)
                )
                .scalars()
                .one_or_none()
            )
        else:
            self.household = None

        if self.username is None:
            self.username = full_name

        self._set_permissions(**kwargs)

    def update_password(self, password):
        self.password = password

    def _set_permissions(
        self, admin, can_manage_household=False, can_manage=False, can_invite=False, can_organize=False, **_
    ):
        """Set user permissions based on the admin flag and the passed in kwargs

        Args:
            admin (bool):
            can_manage_household (bool):
            can_manage (bool):
            can_invite (bool):
            can_organize (bool):
        """
        self.admin = admin
        if self.admin:
            self.can_manage_household = True
            self.can_manage = True
            self.can_invite = True
            self.can_organize = True
            self.advanced = True
        else:
            self.can_manage_household = can_manage_household
            self.can_manage = can_manage
            self.can_invite = can_invite
            self.can_organize = can_organize
