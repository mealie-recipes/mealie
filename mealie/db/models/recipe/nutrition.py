import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class Nutrition(SqlAlchemyBase):
    __tablename__ = "recipe_nutrition"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("recipes.id"), index=True)
    calories: Mapped[str | None] = mapped_column(sa.String)
    fat_content: Mapped[str | None] = mapped_column(sa.String)
    fiber_content: Mapped[str | None] = mapped_column(sa.String)
    protein_content: Mapped[str | None] = mapped_column(sa.String)
    carbohydrate_content: Mapped[str | None] = mapped_column(sa.String)
    sodium_content: Mapped[str | None] = mapped_column(sa.String)
    sugar_content: Mapped[str | None] = mapped_column(sa.String)

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
