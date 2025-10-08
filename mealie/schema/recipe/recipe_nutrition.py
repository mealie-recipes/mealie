from enum import Enum

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from mealie.schema._mealie import MealieModel


class NutritionUnit(str, Enum):
    GRAM = "g"
    MILLIGRAM = "mg"
    KILOCALORIE = "kcal"
    INTERNATIONAL_UNIT = "IU"
    MICROGRAM = "µg"


class Nutrition(MealieModel):
    calories: str | None = None
    calories_unit: str | None = Field("kcal", alias="caloriesUnit")

    carbohydrate_content: str | None = None
    carbohydrate_content_unit: str | None = Field("g", alias="carbohydrateContentUnit")

    cholesterol_content: str | None = None
    cholesterol_content_unit: str | None = Field("mg", alias="cholesterolContentUnit")

    fat_content: str | None = None
    fat_content_unit: str | None = Field("g", alias="fatContentUnit")

    fiber_content: str | None = None
    fiber_content_unit: str | None = Field("g", alias="fiberContentUnit")

    protein_content: str | None = None
    protein_content_unit: str | None = Field("g", alias="proteinContentUnit")

    saturated_fat_content: str | None = None
    saturated_fat_content_unit: str | None = Field("g", alias="saturatedFatContentUnit")

    sodium_content: str | None = None
    sodium_content_unit: str | None = Field("mg", alias="sodiumContentUnit")

    sugar_content: str | None = None
    sugar_content_unit: str | None = Field("g", alias="sugarContentUnit")

    trans_fat_content: str | None = None
    trans_fat_content_unit: str | None = Field("g", alias="transFatContentUnit")

    unsaturated_fat_content: str | None = None
    unsaturated_fat_content_unit: str | None = Field("g", alias="unsaturatedFatContentUnit")

    # NEW: arbitrary custom nutrients (user-defined)
    custom_nutrition: dict[str, dict[str, str]] | None = Field(
        default_factory=dict,
        alias="customNutrition",
    )

    model_config = ConfigDict(
        from_attributes=True,
        coerce_numbers_to_str=True,
        alias_generator=to_camel,
        populate_by_name=True,  # accept both camelCase and snake_case
        ser_json_tuples=True,  # ensure serialization uses aliases
    )


class NutritionUnitsResponse(MealieModel):
    """Response model for available units"""

    units: list[str]
