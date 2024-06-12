from pydantic import ConfigDict, Field

from mealie.schema._mealie.mealie_model import MealieModel


class ScrapeRecipeTest(MealieModel):
    url: str
    use_openai: bool = Field(False, alias="useOpenAI")


class ScrapeRecipe(MealieModel):
    url: str
    include_tags: bool = False
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://myfavoriterecipes.com/recipes",
                "includeTags": True,
            },
        }
    )
