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
