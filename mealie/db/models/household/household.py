from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm
from pydantic import ConfigDict
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from ..users import User
    from . import (
        CookBook,
        GroupEventNotifierModel,
        GroupInviteToken,
        GroupRecipeAction,
        GroupWebhooksModel,
        HouseholdPreferencesModel,
    )


class Household(SqlAlchemyBase, BaseMixins):
    __tablename__ = "households"
    __table_args__ = (
        sa.UniqueConstraint("group_id", "name", name="household_name_group_id_key"),
        sa.UniqueConstraint("group_id", "slug", name="household_slug_group_id_key"),
    )

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    name: Mapped[str] = mapped_column(sa.String, index=True, nullable=False)
    slug: Mapped[str | None] = mapped_column(sa.String, index=True)

    invite_tokens: Mapped[list["GroupInviteToken"]] = orm.relationship(
        "GroupInviteToken", back_populates="household", cascade="all, delete-orphan"
    )
    preferences: Mapped["HouseholdPreferencesModel"] = orm.relationship(
        "HouseholdPreferencesModel",
        back_populates="household",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )

    group_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="households")
    users: Mapped[list["User"]] = orm.relationship("User", back_populates="household")

    COMMON_ARGS = {
        "back_populates": "household",
        "cascade": "all, delete-orphan",
        "single_parent": True,
    }

    recipe_actions: Mapped[list["GroupRecipeAction"]] = orm.relationship("GroupRecipeAction", **COMMON_ARGS)
    cookbooks: Mapped[list["CookBook"]] = orm.relationship("CookBook", **COMMON_ARGS)

    webhooks: Mapped[list["GroupWebhooksModel"]] = orm.relationship("GroupWebhooksModel", **COMMON_ARGS)
    group_event_notifiers: Mapped[list["GroupEventNotifierModel"]] = orm.relationship(
        "GroupEventNotifierModel", **COMMON_ARGS
    )

    model_config = ConfigDict(
        exclude={
            "users",
            "webhooks",
            "recipe_actions",
            "cookbooks",
            "preferences",
            "invite_tokens",
            "group_event_notifiers",
            "group",
        }
    )

    @auto_init()
    def __init__(self, **_) -> None:
        pass
