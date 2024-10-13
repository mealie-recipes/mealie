import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class Nutrition(SqlAlchemyBase):
    __tablename__ = "recipe_nutrition"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("recipes.id"), index=True)

    calories: Mapped[str | None] = mapped_column(sa.String)
    carbohydrate_content: Mapped[str | None] = mapped_column(sa.String)
    cholesterol_content: Mapped[str | None] = mapped_column(sa.String)
    fat_content: Mapped[str | None] = mapped_column(sa.String)
    fiber_content: Mapped[str | None] = mapped_column(sa.String)
    protein_content: Mapped[str | None] = mapped_column(sa.String)
    saturated_fat_content: Mapped[str | None] = mapped_column(sa.String)

    # `serving_size` is not a scaling factor, but a per-serving volume or mass
    # according to schema.org. E.g., "2 L", "500 g", "5 cups", etc.
    #
    # Ignoring for now because it's too difficult to work around variable units
    # in translation for the frontend. Also, it causes cognitive dissonance wrt
    # "servings" (i.e., "serves 2" etc.), which is an unrelated concept that
    # might cause confusion.
    #
    # serving_size: Mapped[str | None] = mapped_column(sa.String)

    sodium_content: Mapped[str | None] = mapped_column(sa.String)
    sugar_content: Mapped[str | None] = mapped_column(sa.String)
    trans_fat_content: Mapped[str | None] = mapped_column(sa.String)
    unsaturated_fat_content: Mapped[str | None] = mapped_column(sa.String)

    def __init__(
        self,
        calories=None,
        carbohydrate_content=None,
        cholesterol_content=None,
        fat_content=None,
        fiber_content=None,
        protein_content=None,
        saturated_fat_content=None,
        sodium_content=None,
        sugar_content=None,
        trans_fat_content=None,
        unsaturated_fat_content=None,
    ) -> None:
        self.calories = calories
        self.carbohydrate_content = carbohydrate_content
        self.cholesterol_content = cholesterol_content
        self.fat_content = fat_content
        self.fiber_content = fiber_content
        self.protein_content = protein_content
        self.saturated_fat_content = saturated_fat_content
        self.sodium_content = sodium_content
        self.sugar_content = sugar_content
        self.trans_fat_content = trans_fat_content
        self.unsaturated_fat_content = unsaturated_fat_content
