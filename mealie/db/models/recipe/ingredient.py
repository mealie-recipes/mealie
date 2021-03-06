import sqlalchemy as sa
from db.models.model_base import SqlAlchemyBase


class RecipeIngredient(SqlAlchemyBase):
    __tablename__ = "recipes_ingredients"
    id = sa.Column(sa.Integer, primary_key=True)
    position = sa.Column(sa.Integer)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    ingredient = sa.Column(sa.String)

    def update(self, ingredient):
        self.ingredient = ingredient

    def to_str(self):
        return self.ingredient
