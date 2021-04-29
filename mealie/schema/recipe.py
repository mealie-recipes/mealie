import datetime
from typing import Any, Optional

from fastapi_camelcase import CamelModel
from mealie.db.models.recipe.recipe import RecipeModel
from pydantic import BaseModel, Field, validator
from pydantic.utils import GetterDict
from slugify import slugify


class RecipeSettings(CamelModel):
    public: bool = True
    show_nutrition: bool = True
    show_assets: bool = True
    landscape_view: bool = True

    class Config:
        orm_mode = True


class RecipeNote(BaseModel):
    title: str
    text: str

    class Config:
        orm_mode = True


class RecipeStep(CamelModel):
    title: Optional[str] = ""
    text: str

    class Config:
        orm_mode = True


class RecipeAsset(CamelModel):
    name: str
    icon: str
    file_name: Optional[str]

    class Config:
        orm_mode = True


class Nutrition(BaseModel):
    calories: Optional[str]
    fatContent: Optional[str]
    proteinContent: Optional[str]
    carbohydrateContent: Optional[str]
    fiberContent: Optional[str]
    sodiumContent: Optional[str]
    sugarContent: Optional[str]

    class Config:
        orm_mode = True


class RecipeSummary(BaseModel):
    id: Optional[int]
    name: str
    slug: Optional[str] = ""
    image: Optional[Any]

    description: Optional[str]
    recipeCategory: Optional[list[str]] = []
    tags: Optional[list[str]] = []
    rating: Optional[int]

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, name_orm: RecipeModel):
            return {
                **GetterDict(name_orm),
                "recipeCategory": [x.name for x in name_orm.recipeCategory],
                "tags": [x.name for x in name_orm.tags],
            }


class Recipe(RecipeSummary):
    recipeYield: Optional[str]
    recipeIngredient: Optional[list[str]]
    recipeInstructions: Optional[list[RecipeStep]]
    nutrition: Optional[Nutrition]
    tools: Optional[list[str]] = []

    totalTime: Optional[str] = None
    prepTime: Optional[str] = None
    performTime: Optional[str] = None

    # Mealie Specific
    settings: Optional[RecipeSettings]
    assets: Optional[list[RecipeAsset]] = []
    dateAdded: Optional[datetime.date]
    notes: Optional[list[RecipeNote]] = []
    orgURL: Optional[str]
    extras: Optional[dict] = {}

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, name_orm: RecipeModel):
            return {
                **GetterDict(name_orm),
                "recipeIngredient": [x.ingredient for x in name_orm.recipeIngredient],
                "recipeCategory": [x.name for x in name_orm.recipeCategory],
                "tags": [x.name for x in name_orm.tags],
                "tools": [x.tool for x in name_orm.tools],
                "extras": {x.key_name: x.value for x in name_orm.extras},
            }

        schema_extra = {
            "example": {
                "name": "Chicken and Rice With Leeks and Salsa Verde",
                "description": "This one-skillet dinner gets deep oniony flavor from lots of leeks cooked down to jammy tenderness.",
                "image": "chicken-and-rice-with-leeks-and-salsa-verde.jpg",
                "recipeYield": "4 Servings",
                "recipeIngredient": [
                    "1 1/2 lb. skinless, boneless chicken thighs (4-8 depending on size)",
                    "Kosher salt, freshly ground pepper",
                    "3 Tbsp. unsalted butter, divided",
                ],
                "recipeInstructions": [
                    {
                        "text": "Season chicken with salt and pepper.",
                    },
                ],
                "slug": "chicken-and-rice-with-leeks-and-salsa-verde",
                "tags": ["favorite", "yummy!"],
                "recipeCategory": ["Dinner", "Pasta"],
                "notes": [{"title": "Watch Out!", "text": "Prep the day before!"}],
                "orgURL": "https://www.bonappetit.com/recipe/chicken-and-rice-with-leeks-and-salsa-verde",
                "rating": 3,
                "extras": {"message": "Don't forget to defrost the chicken!"},
            }
        }

    @validator("slug", always=True, pre=True)
    def validate_slug(slug: str, values):
        name: str = values["name"]
        calc_slug: str = slugify(name)

        if slug != calc_slug:
            slug = calc_slug

        return slug


class AllRecipeRequest(BaseModel):
    properties: list[str]
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
