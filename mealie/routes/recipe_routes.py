from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from models.recipe_models import (
    AllRecipeRequest,
    RecipeResponse,
    RecipeURLIn,
    SlugResponse,
)
from services.image_services import read_image, write_image
from services.recipe_services import Recipe, read_requested_values
from services.scrape_services import create_from_url
from utils.snackbar import SnackResponse

router = APIRouter()


@router.get("/api/all-recipes/", tags=["Recipes"], response_model=RecipeResponse)
async def get_all_recipes(
    keys: Optional[List[str]] = Query(...), num: Optional[int] = 100
):
    """
    Returns key data for all recipes based off the query paramters provided.
    For example, if slug, image, and name are provided you will recieve a list of
    recipes containing the slug, image, and name property. By default, responses
    are limited to 100.

    **Note:** You may experience problems with with query parameters. As an alternative
    you may also use the post method and provide a body.
    See the *Post* method for more details.
    """

    all_recipes = read_requested_values(keys, num)
    return all_recipes


@router.post("/api/all-recipes/", tags=["Recipes"], response_model=RecipeResponse)
async def get_all_recipes_post(body: AllRecipeRequest):
    """
    Returns key data for all recipes based off the body data provided.
    For example, if slug, image, and name are provided you will recieve a list of
    recipes containing the slug, image, and name property.

    Refer to the body example for data formats.

    """

    all_recipes = read_requested_values(body.properties, body.limit)

    return all_recipes


@router.get("/api/recipe/{recipe_slug}/", tags=["Recipes"], response_model=Recipe)
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
@router.post(
    "/api/recipe/create-url/",
    tags=["Recipes"],
    status_code=201,
    response_model=SlugResponse,
)
async def parse_recipe_url(url: RecipeURLIn):
    """ Takes in a URL and attempts to scrape data and load it into the database """

    slug = create_from_url(url.url)

    return slug


@router.post("/api/recipe/create/", tags=["Recipes"], response_model=SlugResponse)
async def create_from_json(data: Recipe) -> str:
    """ Takes in a JSON string and loads data into the database as a new entry"""
    created_recipe = data.save_to_db()

    return created_recipe


@router.post("/api/recipe/{recipe_slug}/update/image/", tags=["Recipes"])
def update_recipe_image(
    recipe_slug: str, image: bytes = File(...), extension: str = Form(...)
):
    """ Removes an existing image and replaces it with the incoming file. """
    response = write_image(recipe_slug, image, extension)

    return response


@router.post("/api/recipe/{recipe_slug}/update/", tags=["Recipes"])
async def update_recipe(recipe_slug: str, data: Recipe):
    """ Updates a recipe by existing slug and data. Data should containt """

    data.update(recipe_slug)

    return {"message": "PLACEHOLDER"}


@router.delete("/api/recipe/{recipe_slug}/delete/", tags=["Recipes"])
async def delete_recipe(recipe_slug: str):
    """ Deletes a recipe by slug """

    try:
        Recipe.delete(recipe_slug)
    except:
        raise HTTPException(
            status_code=404, detail=SnackResponse.error("Unable to Delete Recipe")
        )

    return SnackResponse.success("Recipe Deleted")
