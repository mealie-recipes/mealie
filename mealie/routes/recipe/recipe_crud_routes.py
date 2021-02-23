from db.db_setup import generate_session
from fastapi import APIRouter, Depends, File, Form, HTTPException
from fastapi.logger import logger
from fastapi.responses import FileResponse
from schema.recipe import RecipeURLIn
from services.image_services import read_image, write_image
from services.recipe_services import Recipe
from services.scraper.scraper import create_from_url
from sqlalchemy.orm.session import Session
from schema.snackbar import SnackResponse

router = APIRouter(
    prefix="/api/recipes",
    tags=["Recipe CRUD"],
)


@router.post("/create", status_code=201, response_model=str)
def create_from_json(data: Recipe, db: Session = Depends(generate_session)) -> str:
    """ Takes in a JSON string and loads data into the database as a new entry"""
    new_recipe_slug = data.save_to_db(db)

    return new_recipe_slug


@router.post("/create-url", status_code=201, response_model=str)
def parse_recipe_url(url: RecipeURLIn, db: Session = Depends(generate_session)):
    """ Takes in a URL and attempts to scrape data and load it into the database """

    recipe = create_from_url(url.url)

    recipe.save_to_db(db)

    return recipe.slug


@router.get("/{recipe_slug}", response_model=Recipe)
def get_recipe(recipe_slug: str, db: Session = Depends(generate_session)):
    """ Takes in a recipe slug, returns all data for a recipe """
    recipe = Recipe.get_by_slug(db, recipe_slug)

    return recipe


@router.put("/{recipe_slug}")
def update_recipe(
    recipe_slug: str, data: Recipe, db: Session = Depends(generate_session)
):
    """ Updates a recipe by existing slug and data. """

    new_slug = data.update(db, recipe_slug)

    return new_slug


@router.delete("/{recipe_slug}")
def delete_recipe(recipe_slug: str, db: Session = Depends(generate_session)):
    """ Deletes a recipe by slug """

    try:
        Recipe.delete(db, recipe_slug)
    except:
        raise HTTPException(
            status_code=404, detail=SnackResponse.error("Unable to Delete Recipe")
        )

    return SnackResponse.error(f"Recipe {recipe_slug} Deleted")


@router.get("/{recipe_slug}/image")
async def get_recipe_img(recipe_slug: str):
    """ Takes in a recipe slug, returns the static image """
    recipe_image = read_image(recipe_slug)
    if recipe_image:
        return FileResponse(recipe_image)
    else:
        return


@router.put("/{recipe_slug}/image")
def update_recipe_image(
    recipe_slug: str,
    image: bytes = File(...),
    extension: str = Form(...),
    session: Session = Depends(generate_session),
):
    """ Removes an existing image and replaces it with the incoming file. """
    response = write_image(recipe_slug, image, extension)
    Recipe.update_image(session, recipe_slug, extension)

    return response
