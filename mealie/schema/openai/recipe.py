from pydantic import Field

from ._base import OpenAIBase


class OpenAIRecipeIngredient(OpenAIBase):
    title: str | None = Field(
        None,
        description="Ingredient section title (e.g., 'Dry Ingredients'). Only set on the first item in each section.",
    )

    text: str = Field(
        ...,
        description="The complete ingredient text, e.g., '1 cup of flour' or '2 cups of onions, chopped'.",
    )


class OpenAIRecipeInstruction(OpenAIBase):
    title: str | None = Field(
        None,
        description="Instruction section title. Only set on the first step in each section.",
    )

    text: str = Field(
        ...,
        description=(
            "One instruction step. Do not include numeric prefixes like '1.' or 'Step 1', "
            "but do include word-based prefixes like 'First' or 'Second'."
        ),
    )


class OpenAIRecipeNotes(OpenAIBase):
    title: str | None = Field(
        None,
        description="Note title. Ignore generic titles like 'Note' or 'Info' and leave blank.",
    )

    text: str = Field(
        ...,
        description="The note content, such as tips, variations, or preparation advice.",
    )


class OpenAIRecipeNutrition(OpenAIBase):
    calories: str | None = Field(None, description="Calories per serving, as a number without units.")
    carbohydrate_content: str | None = Field(None, description="Carbohydrates per serving, in grams.")
    cholesterol_content: str | None = Field(None, description="Cholesterol per serving, in milligrams.")
    fat_content: str | None = Field(None, description="Total fat per serving, in grams.")
    fiber_content: str | None = Field(None, description="Fiber per serving, in grams.")
    protein_content: str | None = Field(None, description="Protein per serving, in grams.")
    saturated_fat_content: str | None = Field(None, description="Saturated fat per serving, in grams.")
    sodium_content: str | None = Field(None, description="Sodium per serving, in milligrams.")
    sugar_content: str | None = Field(None, description="Sugar per serving, in grams.")
    trans_fat_content: str | None = Field(None, description="Trans fat per serving, in grams.")
    unsaturated_fat_content: str | None = Field(None, description="Unsaturated fat per serving, in grams.")


class OpenAIRecipe(OpenAIBase):
    name: str = Field(
        ...,
        description="Recipe name or title. Make your best guess if not obvious.",
    )

    description: str | None = Field(
        None,
        description="A brief description of the recipe in a few words or sentences.",
    )

    recipe_yield: str | None = Field(
        None,
        description="Recipe yield, e.g., '12 cookies' or '4 servings'.",
    )

    total_time: str | None = Field(
        None,
        description="Total time as text (e.g., '1 hour 30 minutes'). Use if only one time is available.",
    )

    prep_time: str | None = Field(
        None,
        description="Prep time as text, e.g., '30 minutes'. Do not duplicate total_time.",
    )

    perform_time: str | None = Field(
        None,
        description="Cook/perform time as text, e.g., '1 hour'. Do not duplicate total_time.",
    )

    ingredients: list[OpenAIRecipeIngredient] = Field(
        default_factory=list,
        description="List of ingredients in order.",
    )

    instructions: list[OpenAIRecipeInstruction] = Field(
        default_factory=list,
        description="List of instruction steps in order.",
    )

    notes: list[OpenAIRecipeNotes] = Field(
        default_factory=list,
        description="List of notes, tips, or variations.",
    )

    nutrition: OpenAIRecipeNutrition | None = Field(
        None,
        description="Nutrition information, only if the source provides it. Do not calculate or estimate it.",
    )
