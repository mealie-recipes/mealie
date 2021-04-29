import sqlalchemy as sa
from mealie.db.models.model_base import SqlAlchemyBase


class RecipeIngredient(SqlAlchemyBase):
    __tablename__ = "recipes_ingredients"
    id = sa.Column(sa.Integer, primary_key=True)
    position = sa.Column(sa.Integer)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))
    ingredient = sa.Column(sa.String)

    def update(self, ingredient):
        self.ingredient = ingredient
