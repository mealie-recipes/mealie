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
