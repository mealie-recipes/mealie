from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SocialRecipeIngredient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    originalText: str = Field(..., description="The ingredient exactly as it appeared in the source.")
    quantity: float | None = Field(None, description="Parsed quantity, using decimal numbers for fractions.")
    unit: str | None = Field(None, description="Parsed measurement unit when reasonably clear.")
    food: str | None = Field(None, description="Parsed food name when reasonably clear.")
    note: str | None = Field(None, description="Preparation note or other ingredient detail.")


class SocialRecipeInstruction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    text: str


class SocialRecipe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    sourceUrl: str | None = None
    servings: float | None = None
    prepTimeMinutes: int | None = None
    cookTimeMinutes: int | None = None
    ingredients: list[SocialRecipeIngredient] = Field(default_factory=list)
    instructions: list[SocialRecipeInstruction] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"]
