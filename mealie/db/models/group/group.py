from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm
from pydantic import ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.db.models.labels import MultiPurposeLabel

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init
from ..group.invite_tokens import GroupInviteToken
from ..group.webhooks import GroupWebhooksModel
from ..recipe.category import Category, group_to_categories
from .cookbook import CookBook
from .mealplan import GroupMealPlan
from .preferences import GroupPreferencesModel

if TYPE_CHECKING:
    from ..recipe import (
        IngredientFoodModel,
        IngredientUnitModel,
        RecipeModel,
        Tag,
        Tool,
    )
    from ..server.task import ServerTaskModel
    from ..users import User
    from .events import GroupEventNotifierModel
    from .exports import GroupDataExportsModel
    from .recipe_action import GroupRecipeAction
    from .report import ReportModel
    from .shopping_list import ShoppingList


class Group(SqlAlchemyBase, BaseMixins):
    __tablename__ = "groups"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    name: Mapped[str] = mapped_column(sa.String, index=True, nullable=False, unique=True)
    slug: Mapped[str | None] = mapped_column(sa.String, index=True, unique=True)
    users: Mapped[list["User"]] = orm.relationship("User", back_populates="group")
    categories: Mapped[list[Category]] = orm.relationship(Category, secondary=group_to_categories, single_parent=True)

    invite_tokens: Mapped[list[GroupInviteToken]] = orm.relationship(
        GroupInviteToken, back_populates="group", cascade="all, delete-orphan"
    )
    preferences: Mapped[GroupPreferencesModel] = orm.relationship(
        GroupPreferencesModel,
        back_populates="group",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )

    # Recipes
    recipes: Mapped[list["RecipeModel"]] = orm.relationship("RecipeModel", back_populates="group")

    # CRUD From Others
    common_args = {
        "back_populates": "group",
        "cascade": "all, delete-orphan",
        "single_parent": True,
    }

    labels: Mapped[list[MultiPurposeLabel]] = orm.relationship(MultiPurposeLabel, **common_args)

    mealplans: Mapped[list[GroupMealPlan]] = orm.relationship(
        GroupMealPlan, order_by="GroupMealPlan.date", **common_args
    )
    webhooks: Mapped[list[GroupWebhooksModel]] = orm.relationship(GroupWebhooksModel, **common_args)
    recipe_actions: Mapped[list["GroupRecipeAction"]] = orm.relationship("GroupRecipeAction", **common_args)
    cookbooks: Mapped[list[CookBook]] = orm.relationship(CookBook, **common_args)
    server_tasks: Mapped[list["ServerTaskModel"]] = orm.relationship("ServerTaskModel", **common_args)
    data_exports: Mapped[list["GroupDataExportsModel"]] = orm.relationship("GroupDataExportsModel", **common_args)
    shopping_lists: Mapped[list["ShoppingList"]] = orm.relationship("ShoppingList", **common_args)
    group_reports: Mapped[list["ReportModel"]] = orm.relationship("ReportModel", **common_args)
    group_event_notifiers: Mapped[list["GroupEventNotifierModel"]] = orm.relationship(
        "GroupEventNotifierModel", **common_args
    )

    # Owned Models
    ingredient_units: Mapped[list["IngredientUnitModel"]] = orm.relationship("IngredientUnitModel", **common_args)
    ingredient_foods: Mapped[list["IngredientFoodModel"]] = orm.relationship("IngredientFoodModel", **common_args)
    tools: Mapped[list["Tool"]] = orm.relationship("Tool", **common_args)
    tags: Mapped[list["Tag"]] = orm.relationship("Tag", **common_args)
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
            "data_exports",
        }
    )

    @auto_init()
    def __init__(self, **_) -> None:
        pass

    @staticmethod  # TODO: Remove this
    def get_by_name(session: Session, name: str) -> Optional["Group"]:
        settings = get_app_settings()

        item = session.execute(select(Group).filter(Group.name == name)).scalars().one_or_none()
        if item is None:
            item = session.execute(select(Group).filter(Group.name == settings.DEFAULT_GROUP)).scalars().one_or_none()
        return item
