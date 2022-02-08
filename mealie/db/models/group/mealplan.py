from sqlalchemy import Column, Date, ForeignKey, String, orm
from sqlalchemy.sql.sqltypes import Integer

from mealie.db.models.recipe.tag import Tag, plan_rules_to_tags

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init
from ..recipe.category import Category, plan_rules_to_categories


class GroupMealPlanRules(BaseMixins, SqlAlchemyBase):
    __tablename__ = "group_meal_plan_rules"

    id = Column(GUID, primary_key=True, default=GUID.generate)
    group_id = Column(GUID, ForeignKey("groups.id"), nullable=False)

    day = Column(String, nullable=False, default="unset")  # "MONDAY", "TUESDAY", "WEDNESDAY", etc...
    entry_type = Column(String, nullable=False, default="")  # "breakfast", "lunch", "dinner", "snack"

    categories = orm.relationship(Category, secondary=plan_rules_to_categories, uselist=True)
    tags = orm.relationship(Tag, secondary=plan_rules_to_tags, uselist=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class GroupMealPlan(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_meal_plans"

    date = Column(Date, index=True, nullable=False)
    entry_type = Column(String, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    text = Column(String, nullable=False)

    group_id = Column(GUID, ForeignKey("groups.id"), index=True)
    group = orm.relationship("Group", back_populates="mealplans")

    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    recipe = orm.relationship("RecipeModel", back_populates="meal_entries", uselist=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
