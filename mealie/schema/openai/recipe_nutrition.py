from textwrap import dedent

from pydantic import Field

from mealie.schema.recipe.recipe_nutrition import Nutrition

from ._base import OpenAIBase


class OpenAINutrition(OpenAIBase):
    nutrition: Nutrition | None = Field(
        None,
        description=dedent(
            """
            A dictionary of the nutritional information for the recipe. The dictionary should contain the following:
            Calories, Carbohydrates, Cholesterol, Fat, Fiber, Protein, Saturated fat, Sodium, Sugar, trans-fat,
            and unsaturated fat.
            """
        ),
    )
