from textwrap import dedent
from typing import Any

from pydantic import Field, field_validator

from ._base import OpenAIBase


class OpenAIIngredient(OpenAIBase):
    quantity: float | None = Field(
        0,
        description=dedent(
            """
            The numerical representation of how much of this ingredient. For instance, if you receive
            "3 1/2 grams of minced garlic", the quantity is "3 1/2". Quantity may be represented as a whole number
            (integer), a float or decimal, or a fraction. You should output quantity in only whole numbers or
            floats, converting fractions into floats. Floats longer than 10 decimal places should be
            rounded to 10 decimal places.
            """
        ),
    )
    unit: str | None = Field(
        None,
        description=dedent(
            """
            The unit of measurement for this ingredient. For instance, if you receive
            "2 lbs chicken breast", the unit is "lbs" (short for "pounds").
            """
        ),
    )
    food: str | None = Field(
        None,
        description=dedent(
            """
            The actual physical ingredient used in the recipe. For instance, if you receive
            "3 cups of onions, chopped", the food is "onions".
            """
        ),
    )
    note: str | None = Field(
        None,
        description=dedent(
            """
            The rest of the text that represents more detail on how to prepare the ingredient.
            Anything that is not one of the above should be the note. For instance, if you receive
            "one can of butter beans, drained" the note would be "drained". If you receive
            "3 cloves of garlic peeled and finely chopped", the note would be "peeled and finely chopped".
            """
        ),
    )

    @field_validator("quantity", mode="before")
    def coerce_none_float(cls, v: Any) -> Any:
        return v or 0


class OpenAIIngredients(OpenAIBase):
    ingredients: list[OpenAIIngredient] = []
