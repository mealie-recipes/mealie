from pydantic import ConfigDict

from mealie.schema._mealie import MealieModel


class Nutrition(MealieModel):
    calories: str | None = None
    fat_content: str | None = None
    protein_content: str | None = None
    carbohydrate_content: str | None = None
    fiber_content: str | None = None
    sodium_content: str | None = None
    sugar_content: str | None = None
    model_config = ConfigDict(from_attributes=True, coerce_numbers_to_str=True)
