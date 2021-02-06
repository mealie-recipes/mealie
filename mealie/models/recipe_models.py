from typing import List, Optional

import pydantic
from pydantic.main import BaseModel


class AllRecipeResponse(BaseModel):
    

    class Config:
        schema_extra = {
            "example": [
                {
                    "slug": "crockpot-buffalo-chicken",
                    "image": "crockpot-buffalo-chicken.jpg",
                    "name": "Crockpot Buffalo Chicken",
                },
                {
                    "slug": "downtown-marinade",
                    "image": "downtown-marinade.jpg",
                    "name": "Downtown Marinade",
                },
                {
                    "slug": "detroit-style-pepperoni-pizza",
                    "image": "detroit-style-pepperoni-pizza.jpg",
                    "name": "Detroit-Style Pepperoni Pizza",
                },
                {
                    "slug": "crispy-carrots",
                    "image": "crispy-carrots.jpg",
                    "name": "Crispy Carrots",
                },
            ]
        }


class AllRecipeRequest(BaseModel):
    properties: List[str]
    limit: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "properties": ["name", "slug", "image"],
                "limit": 100,
            }
        }


class RecipeURLIn(BaseModel):
    url: str

    class Config:
        schema_extra = {"example": {"url": "https://myfavoriterecipes.com/recipes"}}


class SlugResponse(BaseModel):
    class Config:
        schema_extra = {"example": "adult-mac-and-cheese"}
