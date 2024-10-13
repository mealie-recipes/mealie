from textwrap import dedent
from typing import Any

from pydantic import Field, field_validator

from ._base import OpenAIBase


class OpenAIIngredient(OpenAIBase):
    input: str = Field(
        ...,
        description=dedent(
            """
            The input is simply the ingredient string you are processing as-is. It is forbidden to
            modify this at all, you must provide the input exactly as you received it.
            """
        ),
    )
    confidence: float | None = Field(
        None,
        description=dedent(
            """
            This value is a float between 0 - 100, where 100 is full confidence that the result is correct,
            and 0 is no confidence that the result is correct. If you're unable to parse anything,
            and you put the entire string in the notes, you should return 0 confidence. If you can easily
            parse the string into each component, then you should return a confidence of 100. If you have to
            guess which part is the unit and which part is the food, your confidence should be lower, such as 60.
            Even if there is no unit or note, if you're able to determine the food, you may use a higher confidence.
            If the entire ingredient consists of only a food, you can use a confidence of 100.
            """
        ),
    )

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

    @field_validator("confidence", "quantity", mode="before")
    def coerce_none_float(cls, v: Any) -> Any:
        return v or 0

    @field_validator("confidence")
    def validate_confidence(cls, v: float | None) -> float:
        v = v or 0

        if v < 0:
            v = 0
        elif v > 100:
            v = 100

        return v / 100


class OpenAIIngredients(OpenAIBase):
    ingredients: list[OpenAIIngredient] = []
