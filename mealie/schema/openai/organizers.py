from pydantic import Field

from ._base import OpenAIBase


class OpenAIOrganizers(OpenAIBase):
    tags: list[str] = Field(
        default_factory=list,
        description="Tags describing the recipe, e.g., 'Vegetarian', 'Quick', 'Weeknight'.",
    )

    categories: list[str] = Field(
        default_factory=list,
        description="Categories the recipe belongs to, e.g., 'Dinner', 'Dessert', 'Breakfast'.",
    )

    tools: list[str] = Field(
        default_factory=list,
        description="Equipment needed to make the recipe, e.g., 'Dutch Oven', 'Stand Mixer'.",
    )
