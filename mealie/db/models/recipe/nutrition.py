import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


class Nutrition(SqlAlchemyBase):
    __tablename__ = "recipe_nutrition"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("recipes.id"), index=True)

    calories: Mapped[str | None] = mapped_column(sa.String)
    calories_unit: Mapped[str | None] = mapped_column(sa.String, default="kcal")

    carbohydrate_content: Mapped[str | None] = mapped_column(sa.String)
    carbohydrate_content_unit: Mapped[str | None] = mapped_column(sa.String, default="g")

    cholesterol_content: Mapped[str | None] = mapped_column(sa.String)
    cholesterol_content_unit: Mapped[str | None] = mapped_column(sa.String, default="mg")

    fat_content: Mapped[str | None] = mapped_column(sa.String)
    fat_content_unit: Mapped[str | None] = mapped_column(sa.String, default="g")

    fiber_content: Mapped[str | None] = mapped_column(sa.String)
    fiber_content_unit: Mapped[str | None] = mapped_column(sa.String, default="g")

    protein_content: Mapped[str | None] = mapped_column(sa.String)
    protein_content_unit: Mapped[str | None] = mapped_column(sa.String, default="g")

    saturated_fat_content: Mapped[str | None] = mapped_column(sa.String)
    saturated_fat_content_unit: Mapped[str | None] = mapped_column(sa.String, default="g")

    sodium_content: Mapped[str | None] = mapped_column(sa.String)
    sodium_content_unit: Mapped[str | None] = mapped_column(sa.String, default="mg")

    sugar_content: Mapped[str | None] = mapped_column(sa.String)
    sugar_content_unit: Mapped[str | None] = mapped_column(sa.String, default="g")

    trans_fat_content: Mapped[str | None] = mapped_column(sa.String)
    trans_fat_content_unit: Mapped[str | None] = mapped_column(sa.String, default="g")

    unsaturated_fat_content: Mapped[str | None] = mapped_column(sa.String)
    unsaturated_fat_content_unit: Mapped[str | None] = mapped_column(sa.String, default="g")

    # NEW: JSON field to hold arbitrary user-defined nutrients
    custom_nutrition: Mapped[dict | None] = mapped_column(sa.JSON, default=dict)

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
        calories_unit="kcal",
        carbohydrate_content_unit="g",
        cholesterol_content_unit="mg",
        fat_content_unit="g",
        fiber_content_unit="g",
        protein_content_unit="g",
        saturated_fat_content_unit="g",
        sodium_content_unit="mg",
        sugar_content_unit="g",
        trans_fat_content_unit="g",
        unsaturated_fat_content_unit="g",
        custom_nutrition=None,  # NEW
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

        self.calories_unit = calories_unit
        self.carbohydrate_content_unit = carbohydrate_content_unit
        self.cholesterol_content_unit = cholesterol_content_unit
        self.fat_content_unit = fat_content_unit
        self.fiber_content_unit = fiber_content_unit
        self.protein_content_unit = protein_content_unit
        self.saturated_fat_content_unit = saturated_fat_content_unit
        self.sodium_content_unit = sodium_content_unit
        self.sugar_content_unit = sugar_content_unit
        self.trans_fat_content_unit = trans_fat_content_unit
        self.unsaturated_fat_content_unit = unsaturated_fat_content_unit

        # NEW
        self.custom_nutrition = custom_nutrition or {}
