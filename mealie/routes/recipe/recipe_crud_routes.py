from fastapi import APIRouter, Depends, File, Form, HTTPException, status
from mealie.core.root_logger import get_logger
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.recipe import Recipe, RecipeURLIn
from mealie.services.image.image import delete_image, rename_image, scrape_image, write_image
from mealie.services.scraper.scraper import create_from_url
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/recipes", tags=["Recipe CRUD"])
logger = get_logger()


@router.post("/create", status_code=201, response_model=str)
def create_from_json(
    data: Recipe,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
) -> str:
    """ Takes in a JSON string and loads data into the database as a new entry"""
    recipe: Recipe = db.recipes.create(session, data.dict())

    return recipe.slug


@router.post("/create-url", status_code=201, response_model=str)
def parse_recipe_url(
    url: RecipeURLIn,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Takes in a URL and attempts to scrape data and load it into the database """

    recipe = create_from_url(url.url)
    recipe: Recipe = db.recipes.create(session, recipe.dict())

    return recipe.slug


@router.get("/{recipe_slug}", response_model=Recipe)
def get_recipe(recipe_slug: str, session: Session = Depends(generate_session)):
    """ Takes in a recipe slug, returns all data for a recipe """

    return db.recipes.get(session, recipe_slug)


@router.put("/{recipe_slug}")
def update_recipe(
    recipe_slug: str,
    data: Recipe,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Updates a recipe by existing slug and data. """

    recipe: Recipe = db.recipes.update(session, recipe_slug, data.dict())
    print(recipe.assets)

    if recipe_slug != recipe.slug:
        rename_image(original_slug=recipe_slug, new_slug=recipe.slug)

    return recipe


@router.patch("/{recipe_slug}")
def patch_recipe(
    recipe_slug: str,
    data: dict,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Updates a recipe by existing slug and data. """

    existing_entry: Recipe = db.recipes.get(session, recipe_slug)

    entry_dict = existing_entry.dict()
    entry_dict.update(data)
    updated_entry = Recipe(**entry_dict)  # ! Surely there's a better way?

    recipe: Recipe = db.recipes.update(session, recipe_slug, updated_entry.dict())

    if recipe_slug != recipe.slug:
        rename_image(original_slug=recipe_slug, new_slug=recipe.slug)

    return recipe


@router.delete("/{recipe_slug}")
def delete_recipe(
    recipe_slug: str,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Deletes a recipe by slug """

    try:
        db.recipes.delete(session, recipe_slug)
        delete_image(recipe_slug)
    except:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@router.put("/{recipe_slug}/image")
def update_recipe_image(
    recipe_slug: str,
    image: bytes = File(...),
    extension: str = Form(...),
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Removes an existing image and replaces it with the incoming file. """
    response = write_image(recipe_slug, image, extension)
    db.recipes.update_image(session, recipe_slug, extension)

    return response


@router.post("/{recipe_slug}/image")
def scrape_image_url(
    recipe_slug: str,
    url: RecipeURLIn,
    current_user=Depends(get_current_user),
):
    """ Removes an existing image and replaces it with the incoming file. """

    scrape_image(url.url, recipe_slug)
