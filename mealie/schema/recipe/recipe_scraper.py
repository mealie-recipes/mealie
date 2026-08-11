from pydantic import ConfigDict, Field

from mealie.schema._mealie.mealie_model import MealieModel


class ScrapeRecipeTest(MealieModel):
    url: str
    use_openai: bool = Field(False, alias="useOpenAI")


class ScrapeRecipeBase(MealieModel):
    include_tags: bool = False
    include_categories: bool = False


class ScrapeRecipe(ScrapeRecipeBase):
    url: str
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://myfavoriterecipes.com/recipes",
                "includeTags": True,
                "includeCategories": True,
            },
        }
    )


class ScrapeRecipeData(ScrapeRecipeBase):
    data: str
    """HTML data or JSON string of a https://schema.org/Recipe object"""

    url: str | None = None
    """Optional URL of the recipe source"""


class ScrapeRecipeAI(MealieModel):
    """Source material for an AI recipe import. At least one field, or one image, is required."""

    content: str | None = None
    """HTML, a JSON string of a https://schema.org/Recipe object, or plain text"""

    url: str | None = None
    """Optional URL of the recipe source. Always fetched, and combined with any other source"""

    translate_language: str | None = None
    """Optional language to translate the recipe into"""

    create_new_organizers: bool = False
    """Whether to create tags, categories, and tools that don't already exist in the group"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "<html>...</html>",
                "url": "https://myfavoriterecipes.com/recipes",
                "translateLanguage": "English",
                "createNewOrganizers": False,
            },
        }
    )
