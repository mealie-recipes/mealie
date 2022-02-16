import sqlalchemy as sa

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class Nutrition(SqlAlchemyBase):
    __tablename__ = "recipe_nutrition"
    id = sa.Column(sa.Integer, primary_key=True)
    recipe_id = sa.Column(GUID, sa.ForeignKey("recipes.id"))
    calories = sa.Column(sa.String)
    fat_content = sa.Column(sa.String)
    fiber_content = sa.Column(sa.String)
    protein_content = sa.Column(sa.String)
    carbohydrate_content = sa.Column(sa.String)
    sodium_content = sa.Column(sa.String)
    sugar_content = sa.Column(sa.String)

    def __init__(
        self,
        calories=None,
        fat_content=None,
        fiber_content=None,
        protein_content=None,
        sodium_content=None,
        sugar_content=None,
        carbohydrate_content=None,
    ) -> None:
        self.calories = calories
        self.fat_content = fat_content
        self.fiber_content = fiber_content
        self.protein_content = protein_content
        self.sodium_content = sodium_content
        self.sugar_content = sugar_content
        self.carbohydrate_content = carbohydrate_content
