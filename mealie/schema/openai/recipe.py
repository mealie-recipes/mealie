from pydantic import Field

from ._base import OpenAIBase


class OpenAIRecipeIngredient(OpenAIBase):
    title: str | None = Field(
        None,
        description="Ingredient section title (e.g., 'Dry Ingredients'). Only set on the first item in each section.",
    )

    quantity: float | None = Field(
        None,
        description="Numeric quantity, e.g. 2.5. Use null if no quantity.",
    )

    unit: str | None = Field(
        None,
        description="Unit of measurement, e.g. 'cup', 'tbsp', 'g', 'ml'. Use null if no unit.",
    )

    food: str | None = Field(
        None,
        description="The food item, e.g. 'flour', 'onion', 'chicken breast'.",
    )

    note: str | None = Field(
        None,
        description="Additional info like 'chopped', 'to taste', 'room temperature'.",
    )

    original_text: str | None = Field(
        None,
        description="The complete original ingredient text as it appears in the recipe.",
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
    calories: str | None = Field(None, description="Calories, e.g. '350'")
    fat_content: str | None = Field(None, description="Total fat in grams, e.g. '12'")
    protein_content: str | None = Field(None, description="Protein in grams, e.g. '25'")
    carbohydrate_content: str | None = Field(None, description="Carbs in grams, e.g. '40'")
    fiber_content: str | None = Field(None, description="Fiber in grams")
    sugar_content: str | None = Field(None, description="Sugar in grams")
    sodium_content: str | None = Field(None, description="Sodium in milligrams")
    cholesterol_content: str | None = Field(None, description="Cholesterol in milligrams")
    saturated_fat_content: str | None = Field(None, description="Saturated fat in grams")
    trans_fat_content: str | None = Field(None, description="Trans fat in grams")
    unsaturated_fat_content: str | None = Field(None, description="Unsaturated fat in grams")


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
        description="Nutritional information per serving, if available.",
    )
