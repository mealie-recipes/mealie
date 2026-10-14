from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mealie.schema._mealie import MealieModel

# TODO: Should these exist?!?!?!?!?


class RecipeSlug(MealieModel):
    slug: str


class SlugResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": "adult-mac-and-cheese"})


class UpdateImageResponse(BaseModel):
    image: str


class RecipeDuplicate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    as_variant: bool = Field(False, alias="asVariant")
    cooking_method: str | None = Field(None, alias="cookingMethod")

    @model_validator(mode="after")
    def validate_variant(self) -> Self:
        if self.as_variant:
            self.cooking_method = (self.cooking_method or "").strip()
            if not self.cooking_method:
                raise ValueError("A cooking method is required when creating a recipe variant")
        return self
