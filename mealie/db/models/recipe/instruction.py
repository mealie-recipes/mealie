from sqlalchemy import Column, ForeignKey, Integer, String, orm

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init
from .._model_utils.guid import GUID


class RecipeIngredientRefLink(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_ingredient_ref_link"
    instruction_id = Column(Integer, ForeignKey("recipe_instructions.id"))
    reference_id = Column(GUID())

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class RecipeInstruction(SqlAlchemyBase):
    __tablename__ = "recipe_instructions"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("recipes.id"))
    position = Column(Integer)
    type = Column(String, default="")
    title = Column(String)
    text = Column(String)

    ingredient_references = orm.relationship("RecipeIngredientRefLink", cascade="all, delete-orphan")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
