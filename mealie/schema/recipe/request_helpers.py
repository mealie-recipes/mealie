from fastapi_camelcase import CamelModel
from pydantic import BaseModel

# TODO: Should these exist?!?!?!?!?


class RecipeSlug(CamelModel):
    slug: str


class SlugResponse(BaseModel):
    class Config:
        schema_extra = {"example": "adult-mac-and-cheese"}
