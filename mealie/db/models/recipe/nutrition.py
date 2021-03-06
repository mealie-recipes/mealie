import sqlalchemy as sa
from db.models.model_base import SqlAlchemyBase


class Nutrition(SqlAlchemyBase):
    __tablename__ = "recipe_nutrition"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    calories = sa.Column(sa.Integer)
    fatContent = sa.Column(sa.Integer)
    fiberContent = sa.Column(sa.Integer)
    proteinContent = sa.Column(sa.Integer)
    sodiumContent = sa.Column(sa.Integer)
    sugarContent = sa.Column(sa.Integer)

    def __init__(
        self,
        calories=None,
        fatContent=None,
        fiberContent=None,
        proteinContent=None,
        sodiumContent=None,
        sugarContent=None,
    ) -> None:
        self.calories = calories
        self.fatContent = fatContent
        self.fiberContent = fiberContent
        self.proteinContent = proteinContent
        self.sodiumContent = sodiumContent
        self.sugarContent = sugarContent

    def dict(self) -> dict:
        return {
            "calories": self.calories,
            "fatContent": self.fatContent,
            "fiberContent": self.fiberContent,
            "proteinContent": self.proteinContent,
            "sodiumContent": self.sodiumContent,
            "sugarContent": self.sugarContent,
        }
