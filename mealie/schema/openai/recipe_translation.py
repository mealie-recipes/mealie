from pydantic import Field

from ._base import OpenAIBase


class OpenAITranslatedString(OpenAIBase):
    key: str = Field(
        ...,
        description="The exact key from the source item. Return it unchanged so the translation can be matched back.",
    )
    value: str = Field(
        ...,
        description="The translated text for this key.",
    )


class OpenAITranslatedRecipe(OpenAIBase):
    """
    A translation of a recipe's free-text fields. Each list mirrors the keyed items sent in the request;
    return every key you were given, unchanged, paired with its translation. Do not add or drop keys.
    """

    name: str | None = Field(None, description="Translated recipe name.")
    description: str | None = Field(None, description="Translated recipe description.")
    recipe_yield: str | None = Field(None, description="Translated recipe yield, e.g. '4 servings'.")

    instructions: list[OpenAITranslatedString] = Field(
        default_factory=list,
        description="Translated instruction steps, keyed by the step key from the request.",
    )
    instruction_titles: list[OpenAITranslatedString] = Field(
        default_factory=list,
        description="Translated instruction section titles, keyed by the step key from the request.",
    )
    ingredients: list[OpenAITranslatedString] = Field(
        default_factory=list,
        description="Translated ingredient text, keyed by the ingredient key from the request.",
    )
    ingredient_foods: list[OpenAITranslatedString] = Field(
        default_factory=list,
        description="Translated ingredient food names (e.g. 'cucumber' -> 'pepino'), "
        "keyed by the ingredient key from the request.",
    )
    ingredient_units: list[OpenAITranslatedString] = Field(
        default_factory=list,
        description="Translated ingredient unit names (e.g. 'tablespoon' -> 'cucharada'), "
        "keyed by the ingredient key from the request.",
    )
    notes: list[OpenAITranslatedString] = Field(
        default_factory=list,
        description="Translated note text, keyed by the note key from the request.",
    )
    note_titles: list[OpenAITranslatedString] = Field(
        default_factory=list,
        description="Translated note titles, keyed by the note key from the request.",
    )
