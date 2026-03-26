from typing import Any

from pydantic import Field, field_validator

from ._base import OpenAIBase


class OpenAIIngredient(OpenAIBase):
    quantity: float | None = Field(
        0,
        description="The numerical quantity as a whole number or float. Convert fractions to decimals.",
    )
    unit: str | None = Field(
        None,
        description="The unit of measurement, e.g., 'cups', 'lbs', 'teaspoons'.",
    )
    food: str | None = Field(
        None,
        description="The ingredient itself, e.g., 'onions' or 'chicken breast'.",
    )
    note: str | None = Field(
        None,
        description=(
            "Preparation details, e.g., 'chopped', 'drained', 'peeled and minced'. "
            "If there are any elements you're not sure about, put them here."
        ),
    )

    @field_validator("quantity", mode="before")
    def coerce_none_float(cls, v: Any) -> Any:
        return v or 0


class OpenAIIngredients(OpenAIBase):
    ingredients: list[OpenAIIngredient] = Field(
        default_factory=list,
        description="List of parsed ingredients.",
    )
