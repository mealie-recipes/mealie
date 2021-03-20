import sqlalchemy as sa
from mealie.db.models.model_base import SqlAlchemyBase


class RecipeInstruction(SqlAlchemyBase):
    __tablename__ = "recipe_instructions"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    position = sa.Column(sa.Integer)
    type = sa.Column(sa.String, default="")
    text = sa.Column(sa.String)
