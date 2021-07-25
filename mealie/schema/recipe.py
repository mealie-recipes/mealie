import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from fastapi_camelcase import CamelModel
from mealie.core.config import app_dirs, settings
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.schema.comments import CommentOut
from pydantic import BaseModel, Field, validator
from pydantic.utils import GetterDict
from slugify import slugify


class RecipeImageTypes(str, Enum):
    original = "original.webp"
    min = "min-original.webp"
    tiny = "tiny-original.webp"


class RecipeSettings(CamelModel):
    public: bool = settings.RECIPE_PUBLIC
    show_nutrition: bool = settings.RECIPE_SHOW_NUTRITION
    show_assets: bool = settings.RECIPE_SHOW_ASSETS
    landscape_view: bool = settings.RECIPE_LANDSCAPE_VIEW
    disable_comments: bool = settings.RECIPE_DISABLE_COMMENTS
    disable_amount: bool = settings.RECIPE_DISABLE_AMOUNT

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


class Nutrition(CamelModel):
    calories: Optional[str]
    fat_content: Optional[str]
    protein_content: Optional[str]
    carbohydrate_content: Optional[str]
    fiber_content: Optional[str]
    sodium_content: Optional[str]
    sugar_content: Optional[str]

    class Config:
        orm_mode = True


class RecipeIngredientFood(CamelModel):
    name: str = ""
    description: str = ""

    class Config:
        orm_mode = True


class RecipeIngredientUnit(RecipeIngredientFood):
    pass


class RecipeIngredient(CamelModel):
    title: Optional[str]
    note: Optional[str]
    unit: Optional[RecipeIngredientUnit]
    food: Optional[RecipeIngredientFood]
    disable_amount: bool = True
    quantity: int = 1

    class Config:
        orm_mode = True


class RecipeSummary(CamelModel):
    id: Optional[int]
    name: Optional[str]
    slug: str = ""
    image: Optional[Any]

    description: Optional[str]
    recipe_category: Optional[list[str]] = []
    tags: Optional[list[str]] = []
    rating: Optional[int]

    date_added: Optional[datetime.date]
    date_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, name_orm: RecipeModel):
            return {
                **GetterDict(name_orm),
                "recipe_category": [x.name for x in name_orm.recipe_category],
                "tags": [x.name for x in name_orm.tags],
            }


class Recipe(RecipeSummary):
    recipe_yield: Optional[str]
    recipe_ingredient: Optional[list[RecipeIngredient]]
    recipe_instructions: Optional[list[RecipeStep]]
    nutrition: Optional[Nutrition]
    tools: Optional[list[str]] = []

    total_time: Optional[str] = None
    prep_time: Optional[str] = None
    perform_time: Optional[str] = None

    # Mealie Specific
    settings: Optional[RecipeSettings] = RecipeSettings()
    assets: Optional[list[RecipeAsset]] = []
    notes: Optional[list[RecipeNote]] = []
    org_url: Optional[str] = Field(None, alias="orgURL")
    extras: Optional[dict] = {}

    comments: Optional[list[CommentOut]] = []

    @staticmethod
    def directory_from_slug(slug) -> Path:
        return app_dirs.RECIPE_DATA_DIR.joinpath(slug)

    @property
    def directory(self) -> Path:
        dir = app_dirs.RECIPE_DATA_DIR.joinpath(self.slug)
        dir.mkdir(exist_ok=True, parents=True)
        return dir

    @property
    def asset_dir(self) -> Path:
        dir = self.directory.joinpath("assets")
        dir.mkdir(exist_ok=True, parents=True)
        return dir

    @property
    def image_dir(self) -> Path:
        dir = self.directory.joinpath("images")
        dir.mkdir(exist_ok=True, parents=True)
        return dir

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, name_orm: RecipeModel):
            return {
                **GetterDict(name_orm),
                # "recipe_ingredient": [x.note for x in name_orm.recipe_ingredient],
                "recipe_category": [x.name for x in name_orm.recipe_category],
                "tags": [x.name for x in name_orm.tags],
                "tools": [x.tool for x in name_orm.tools],
                "extras": {x.key_name: x.value for x in name_orm.extras},
            }

        schema_extra = {
            "example": {
                "name": "Chicken and Rice With Leeks and Salsa Verde",
                "description": "This one-skillet dinner gets deep oniony flavor from lots of leeks cooked down to jammy tenderness.",
                "image": "chicken-and-rice-with-leeks-and-salsa-verde.jpg",
                "recipe_yield": "4 Servings",
                "recipe_ingredient": [
                    "1 1/2 lb. skinless, boneless chicken thighs (4-8 depending on size)",
                    "Kosher salt, freshly ground pepper",
                    "3 Tbsp. unsalted butter, divided",
                ],
                "recipe_instructions": [
                    {
                        "text": "Season chicken with salt and pepper.",
                    },
                ],
                "slug": "chicken-and-rice-with-leeks-and-salsa-verde",
                "tags": ["favorite", "yummy!"],
                "recipe_category": ["Dinner", "Pasta"],
                "notes": [{"title": "Watch Out!", "text": "Prep the day before!"}],
                "org_url": "https://www.bonappetit.com/recipe/chicken-and-rice-with-leeks-and-salsa-verde",
                "rating": 3,
                "extras": {"message": "Don't forget to defrost the chicken!"},
            }
        }

    @validator("slug", always=True, pre=True)
    def validate_slug(slug: str, values):
        if not values["name"]:
            return slug
        name: str = values["name"]
        calc_slug: str = slugify(name)

        if slug != calc_slug:
            slug = calc_slug

        return slug

    @validator("recipe_ingredient", always=True, pre=True)
    def validate_ingredients(recipe_ingredient, values):
        if not recipe_ingredient or not isinstance(recipe_ingredient, list):
            return recipe_ingredient

        if all(isinstance(elem, str) for elem in recipe_ingredient):
            return [RecipeIngredient(note=x) for x in recipe_ingredient]

        return recipe_ingredient


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
