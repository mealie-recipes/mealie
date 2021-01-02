from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from services.image_services import read_image, write_image
from services.recipe_services import Recipe, read_requested_values
from services.scrape_services import create_from_url
from utils.snackbar import SnackResponse

router = APIRouter()


@router.get("/api/all-recipes/", tags=["Recipes"])
async def get_all_recipes(
    keys: Optional[List[str]] = Query(...), num: Optional[int] = 100
) -> Optional[List[str]]:
    """ Returns key data for all recipes """

    all_recipes = read_requested_values(keys, num)
    return all_recipes


@router.get("/api/recipe/{recipe_slug}/", tags=["Recipes"])
async def get_recipe(recipe_slug: str):
    """ Takes in a recipe slug, returns all data for a recipe """
    recipe = Recipe.get_by_slug(recipe_slug)
    
    return recipe


@router.get("/api/recipe/image/{recipe_slug}/", tags=["Recipes"])
async def get_recipe_img(recipe_slug: str):
    """ Takes in a recipe slug, returns the static image """
    recipe_image = read_image(recipe_slug)

    return FileResponse(recipe_image)


# Recipe Creations
@router.post("/api/recipe/create-url/", tags=["Recipes"])
async def get_recipe_url(url: dict):
    """ Takes in a URL and Attempts to scrape data and load it into the database """

    url = url.get("url")

    try:
        slug = create_from_url(url)
    except:
        raise HTTPException(
            status_code=400, detail=SnackResponse.error("Unable to Parse URL")
        )

    return slug


@router.post("/api/recipe/create/", tags=["Recipes"])
async def create_from_json(data: Recipe) -> str:
    """ Takes in a JSON string and loads data into the database as a new entry"""
    created_recipe = data.save_to_db()

    return created_recipe


@router.post("/api/recipe/{recipe_slug}/update/image/", tags=["Recipes"])
def update_image(
    recipe_slug: str, image: bytes = File(...), extension: str = Form(...)
):
    """ Removes an existing image and replaces it with the incoming file. """
    response = write_image(recipe_slug, image, extension)

    return response


@router.post("/api/recipe/{recipe_slug}/update/", tags=["Recipes"])
async def update(recipe_slug: str, data: dict):
    """ Updates a recipe by existing slug and data. Data should containt """
    Recipe.update(recipe_slug, data)
    return {"message": "PLACEHOLDER"}


@router.delete("/api/recipe/{recipe_slug}/delete/", tags=["Recipes"])
async def delete(recipe_slug: str):
    """ Deletes a recipe by slug """

    try:
        Recipe.delete(recipe_slug)
    except:
        raise HTTPException(
            status_code=404, detail=SnackResponse.error("Unable to Delete Recipe")
        )

    return SnackResponse.success("Recipe Deleted")
