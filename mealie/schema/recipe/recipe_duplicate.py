from pydantic import UUID4, Field

from mealie.schema._mealie.mealie_model import MealieModel


class DuplicateIngredientIn(MealieModel):
    name: str | None = Field(default=None, description="Food name of the ingredient")
    quantity: float | None = Field(default=None, description="Quantity of the ingredient")
    unit: str | None = Field(default=None, description="Unit of measurement")


class RecipeDuplicateCheckIn(MealieModel):
    recipe_id: UUID4 | None = Field(default=None, description="Current recipe ID if editing an existing recipe")
    name: str | None = Field(default=None, description="Recipe name to check for duplicates")
    url: str | None = Field(default=None, description="Original recipe URL to check for duplicates")
    ingredients: list[DuplicateIngredientIn] = Field(
        default_factory=list, description="Ingredients to compare against existing recipes"
    )


class RecipeDuplicateMatchOut(MealieModel):
    id: UUID4
    name: str
    slug: str
    org_url: str | None = None
    similarity_score: float = Field(default=1.0, description="Similarity score between 0.0 and 1.0")
    match_reason: str = Field(description="Reason for match: 'Exact name', 'Matching name and ingredients', etc.")
    matching_ingredients: list[str] = Field(default_factory=list, description="List of matching ingredient foods")


class RecipeDuplicateCheckOut(MealieModel):
    is_duplicate: bool
    matches: list[RecipeDuplicateMatchOut] = Field(default_factory=list)
