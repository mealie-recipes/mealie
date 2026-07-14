from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SocialRecipeIngredient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    originalText: str = Field(..., description="The ingredient exactly as it appeared in the source.")
    quantity: float | None = Field(
        ...,
        description=(
            "Parsed numeric quantity. This MUST be populated when originalText contains an explicit numeric, "
            "decimal, or fractional amount. Convert fractions to decimals only here."
        ),
    )
    unit: str | None = Field(
        ...,
        description=(
            "Parsed measurement unit. This MUST be populated when originalText contains a clear unit such as "
            "tbsp, tsp, g, kg, ml, L, cup, clove, or large."
        ),
    )
    food: str | None = Field(
        ...,
        description="Parsed food name with quantity and unit removed. Populate whenever a food can be identified.",
    )
    note: str | None = Field(
        ...,
        description="Preparation note or other ingredient detail that is not quantity, unit, or food.",
    )


class SocialRecipeInstruction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None
    text: str


class SocialRecipe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None
    sourceUrl: str | None
    servings: float | None
    prepTimeMinutes: int | None
    cookTimeMinutes: int | None
    ingredients: list[SocialRecipeIngredient]
    instructions: list[SocialRecipeInstruction]
    tags: list[str]
    warnings: list[str]
    confidence: Literal["high", "medium", "low"]
