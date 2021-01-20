from typing import List, Optional

from db.db_setup import generate_session
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from models.recipe_models import AllRecipeRequest, RecipeURLIn
from services.image_services import read_image, write_image
from services.recipe_services import Recipe, read_requested_values
from services.scrape_services import create_from_url
from sqlalchemy.orm.session import Session
from utils.snackbar import SnackResponse

router = APIRouter(tags=["Recipes"])


@router.get("/api/all-recipes/", response_model=List[dict])
def get_all_recipes(
    keys: Optional[List[str]] = Query(...),
    num: Optional[int] = 100,
    db: Session = Depends(generate_session),
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

    all_recipes = read_requested_values(db, keys, num)
    return all_recipes


@router.post("/api/all-recipes/", response_model=List[dict])
def get_all_recipes_post(
    body: AllRecipeRequest, db: Session = Depends(generate_session)
):
    """
    Returns key data for all recipes based off the body data provided.
    For example, if slug, image, and name are provided you will recieve a list of
    recipes containing the slug, image, and name property.

    Refer to the body example for data formats.

    """

    all_recipes = read_requested_values(db, body.properties, body.limit)

    return all_recipes


@router.get("/api/recipe/{recipe_slug}/", response_model=Recipe)
def get_recipe(recipe_slug: str, db: Session = Depends(generate_session)):
    """ Takes in a recipe slug, returns all data for a recipe """
    recipe = Recipe.get_by_slug(db, recipe_slug)

    return recipe


@router.get("/api/recipe/image/{recipe_slug}/")
def get_recipe_img(recipe_slug: str):
    """ Takes in a recipe slug, returns the static image """
    recipe_image = read_image(recipe_slug)

    return FileResponse(recipe_image)


# Recipe Creations
@router.post(
    "/api/recipe/create-url/",
    status_code=201,
    response_model=str,
)
def parse_recipe_url(url: RecipeURLIn, db: Session = Depends(generate_session)):
    """ Takes in a URL and attempts to scrape data and load it into the database """

    recipe = create_from_url(url.url)
    recipe.save_to_db(db)

    return recipe.slug


@router.post("/api/recipe/create/")
def create_from_json(data: Recipe, db: Session = Depends(generate_session)) -> str:
    """ Takes in a JSON string and loads data into the database as a new entry"""
    new_recipe_slug = data.save_to_db(db)

    return new_recipe_slug


@router.post("/api/recipe/{recipe_slug}/update/image/")
def update_recipe_image(
    recipe_slug: str, image: bytes = File(...), extension: str = Form(...)
):
    """ Removes an existing image and replaces it with the incoming file. """
    response = write_image(recipe_slug, image, extension)
    Recipe.update_image(recipe_slug, extension)

    return response


@router.post("/api/recipe/{recipe_slug}/update/")
def update_recipe(
    recipe_slug: str, data: Recipe, db: Session = Depends(generate_session)
):
    """ Updates a recipe by existing slug and data. """

    new_slug = data.update(db, recipe_slug)

    return new_slug


@router.delete("/api/recipe/{recipe_slug}/delete/")
def delete_recipe(recipe_slug: str, db: Session = Depends(generate_session)):
    """ Deletes a recipe by slug """

    try:
        Recipe.delete(db, recipe_slug)
    except:
        raise HTTPException(
            status_code=404, detail=SnackResponse.error("Unable to Delete Recipe")
        )

    return SnackResponse.success("Recipe Deleted")
