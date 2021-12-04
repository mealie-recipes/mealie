from sqlalchemy import Column, Date, ForeignKey, String, orm
from sqlalchemy.sql.sqltypes import Integer

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init


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
