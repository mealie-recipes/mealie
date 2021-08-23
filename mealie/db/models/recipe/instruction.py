from mealie.db.models._model_base import SqlAlchemyBase
from sqlalchemy import Column, ForeignKey, Integer, String


class RecipeInstruction(SqlAlchemyBase):
    __tablename__ = "recipe_instructions"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("recipes.id"))
    position = Column(Integer)
    type = Column(String, default="")
    title = Column(String)
    text = Column(String)
