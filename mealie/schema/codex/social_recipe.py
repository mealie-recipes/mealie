from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SocialRecipeIngredient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    originalText: str = Field(..., description="The ingredient exactly as it appeared in the source.")
    quantity: float | None = Field(..., description="Parsed quantity, using decimal numbers for fractions.")
    unit: str | None = Field(..., description="Parsed measurement unit when reasonably clear.")
    food: str | None = Field(..., description="Parsed food name when reasonably clear.")
    note: str | None = Field(..., description="Preparation note or other ingredient detail.")


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
