from mealie.db.models.model_base import SqlAlchemyBase
from sqlalchemy import Column, ForeignKey, Integer, String


class RecipeIngredient(SqlAlchemyBase):
    __tablename__ = "recipes_ingredients"
    id = Column(Integer, primary_key=True)
    position = Column(Integer)
    parent_id = Column(Integer, ForeignKey("recipes.id"))
    # title = Column(String)
    ingredient = Column(String)

    def update(self, ingredient):
        self.ingredient = ingredient
