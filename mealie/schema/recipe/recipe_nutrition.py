from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from mealie.schema._mealie import MealieModel


class Nutrition(MealieModel):
    calories: str | None = None
    carbohydrate_content: str | None = None
    cholesterol_content: str | None = None
    fat_content: str | None = None
    fiber_content: str | None = None
    protein_content: str | None = None
    saturated_fat_content: str | None = None
    sodium_content: str | None = None
    sugar_content: str | None = None
    trans_fat_content: str | None = None
    unsaturated_fat_content: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        coerce_numbers_to_str=True,
        alias_generator=to_camel,
    )
