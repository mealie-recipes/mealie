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
    from ..recipe import RecipeModel
    from ..users import User
    from . import (
        CookBook,
        GroupEventNotifierModel,
        GroupInviteToken,
        GroupMealPlan,
        GroupRecipeAction,
        GroupWebhooksModel,
        ShoppingList,
    )


class Household(SqlAlchemyBase, BaseMixins):
    __tablename__ = "households"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    name: Mapped[str] = mapped_column(sa.String, index=True, nullable=False, unique=True)
    slug: Mapped[str | None] = mapped_column(sa.String, index=True, unique=True)

    invite_tokens: Mapped[list["GroupInviteToken"]] = orm.relationship(
        "GroupInviteToken", back_populates="household", cascade="all, delete-orphan"
    )
    preferences = None  # TODO

    group_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="households")
    users: Mapped[list["User"]] = orm.relationship("User", back_populates="household")

    COMMON_ARGS = {
        "back_populates": "household",
        "cascade": "all, delete-orphan",
        "single_parent": True,
    }

    recipes: Mapped[list["RecipeModel"]] = orm.relationship("RecipeModel", back_populates="household")
    recipe_actions: Mapped[list["GroupRecipeAction"]] = orm.relationship("GroupRecipeAction", **COMMON_ARGS)
    cookbooks: Mapped[list["CookBook"]] = orm.relationship("CookBook", **COMMON_ARGS)

    mealplans: Mapped[list["GroupMealPlan"]] = orm.relationship(
        "GroupMealPlan", order_by="GroupMealPlan.date", **COMMON_ARGS
    )
    shopping_lists: Mapped[list["ShoppingList"]] = orm.relationship("ShoppingList", **COMMON_ARGS)

    webhooks: Mapped[list["GroupWebhooksModel"]] = orm.relationship("GroupWebhooksModel", **COMMON_ARGS)
    group_event_notifiers: Mapped[list["GroupEventNotifierModel"]] = orm.relationship(
        "GroupEventNotifierModel", **COMMON_ARGS
    )

    model_config = ConfigDict(
        exclude={
            "users",
            "webhooks",
            "recipe_actions",
            "shopping_lists",
            "cookbooks",
            "preferences",
            "invite_tokens",
            "mealplans",
        }
    )

    @auto_init()
    def __init__(self, **_) -> None:
        pass
