import datetime
from pathlib import Path
from typing import Any, List, Optional

from db.database import db
from pydantic import BaseModel, validator
from slugify import slugify
from sqlalchemy.orm.session import Session

from services.image_services import delete_image


class RecipeNote(BaseModel):
    title: str
    text: str


class RecipeStep(BaseModel):
    text: str


class Nutrition(BaseModel):
    calories: Optional[int]
    fatContent: Optional[int]
    fiberContent: Optional[int]
    proteinContent: Optional[int]
    sodiumContent: Optional[int]
    sugarContent: Optional[int]


class Recipe(BaseModel):
    # Standard Schema
    name: str
    description: Optional[str]
    image: Optional[Any]
    nutrition: Optional[Nutrition]
    recipeYield: Optional[str]
    recipeCategory: Optional[List[str]] = []
    recipeIngredient: Optional[list]
    recipeInstructions: Optional[list]
    tool: Optional[list[str]]

    totalTime: Optional[str] = None
    prepTime: Optional[str] = None
    performTime: Optional[str] = None

    # Mealie Specific
    slug: Optional[str] = ""
    tags: Optional[List[str]] = []
    dateAdded: Optional[datetime.date]
    notes: Optional[List[RecipeNote]] = []
    rating: Optional[int] = 0
    orgURL: Optional[str] = ""
    extras: Optional[dict] = {}

    class Config:
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

        if slug == calc_slug:
            return slug
        else:
            slug = calc_slug
            return slug

    @classmethod
    def get_by_slug(cls, session, slug: str):
        """ Returns a Recipe Object by Slug """

        document = db.recipes.get(session, slug, "slug")

        return cls(**document)

    def save_to_db(self, session) -> str:
        recipe_dict = self.dict()

        try:
            extension = Path(recipe_dict["image"]).suffix
            recipe_dict["image"] = recipe_dict.get("slug") + extension
        except:
            recipe_dict["image"] = "no image"

        recipe_doc = db.recipes.create(session, recipe_dict)
        recipe = Recipe(**recipe_doc)

        return recipe.slug

    @staticmethod
    def delete(session: Session, recipe_slug: str) -> str:
        """ Removes the recipe from the database by slug """
        delete_image(recipe_slug)
        db.recipes.delete(session, recipe_slug)
        return "Document Deleted"

    def update(self, session: Session, recipe_slug: str):
        """ Updates the recipe from the database by slug"""
        updated_slug = db.recipes.update(session, recipe_slug, self.dict())
        return updated_slug.get("slug")

    @staticmethod
    def update_image(session: Session, slug: str, extension: str = None) -> str:
        """A helper function to pass the new image name and extension
        into the database.

        Args:
            slug (str): The current recipe slug
            extension (str): the file extension of the new image
        """
        return db.recipes.update_image(session, slug, extension)

    @staticmethod
    def get_all(session: Session):
        return db.recipes.get_all(session)
