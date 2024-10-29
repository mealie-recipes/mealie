import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, Date, ForeignKey, String, Table, UniqueConstraint, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models.recipe.tag import Tag, plan_rules_to_tags

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID
from ..recipe.category import Category, plan_rules_to_categories

if TYPE_CHECKING:
    from ..group import Group
    from ..recipe import RecipeModel
    from ..users import User
    from .household import Household

plan_rules_to_households = Table(
    "plan_rules_to_households",
    SqlAlchemyBase.metadata,
    Column("group_plan_rule_id", GUID, ForeignKey("group_meal_plan_rules.id"), index=True),
    Column("household_id", GUID, ForeignKey("households.id"), index=True),
    UniqueConstraint("group_plan_rule_id", "household_id", name="group_plan_rule_id_household_id_key"),
)


class GroupMealPlanRules(BaseMixins, SqlAlchemyBase):
    __tablename__ = "group_meal_plan_rules"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    household_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("households.id"), index=True)

    day: Mapped[str] = mapped_column(
        String, nullable=False, default="unset"
    )  # "MONDAY", "TUESDAY", "WEDNESDAY", etc...
    entry_type: Mapped[str] = mapped_column(
        String, nullable=False, default=""
    )  # "breakfast", "lunch", "dinner", "side"
    query_filter_string: Mapped[str] = mapped_column(String, nullable=False, default="")

    # Old filters - deprecated in favor of query filter strings
    categories: Mapped[list[Category]] = orm.relationship(Category, secondary=plan_rules_to_categories)
    tags: Mapped[list[Tag]] = orm.relationship(Tag, secondary=plan_rules_to_tags)
    households: Mapped[list["Household"]] = orm.relationship("Household", secondary=plan_rules_to_households)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class GroupMealPlan(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_meal_plans"

    date: Mapped[datetime.date] = mapped_column(Date, index=True, nullable=False)
    entry_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)

    group_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("groups.id"), index=True)
    group: Mapped[Optional["Group"]] = orm.relationship("Group", back_populates="mealplans")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")
    household: AssociationProxy["Household"] = association_proxy("user", "household")
    user_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("users.id"), index=True)
    user: Mapped[Optional["User"]] = orm.relationship("User", back_populates="mealplans")

    recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"), index=True)
    recipe: Mapped[Optional["RecipeModel"]] = orm.relationship(
        "RecipeModel", back_populates="meal_entries", uselist=False
    )

    @auto_init()
    def __init__(self, **_) -> None:
        pass
