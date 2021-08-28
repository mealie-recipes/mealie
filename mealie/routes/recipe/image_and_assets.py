from shutil import copyfileobj

from fastapi import Depends, File, Form, HTTPException, status
from fastapi.datastructures import UploadFile
from slugify import slugify
from sqlalchemy.orm.session import Session

from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe import CreateRecipeByURL, Recipe, RecipeAsset
from mealie.services.image.image import scrape_image, write_image

user_router = UserAPIRouter()


@user_router.post("/{recipe_slug}/image")
def scrape_image_url(
    recipe_slug: str,
    url: CreateRecipeByURL,
):
    """ Removes an existing image and replaces it with the incoming file. """

    scrape_image(url.url, recipe_slug)


@user_router.put("/{recipe_slug}/image")
def update_recipe_image(
    recipe_slug: str,
    image: bytes = File(...),
    extension: str = Form(...),
    session: Session = Depends(generate_session),
):
    """ Removes an existing image and replaces it with the incoming file. """
    write_image(recipe_slug, image, extension)
    new_version = db.recipes.update_image(session, recipe_slug, extension)

    return {"image": new_version}


@user_router.post("/{recipe_slug}/assets", response_model=RecipeAsset)
def upload_recipe_asset(
    recipe_slug: str,
    name: str = Form(...),
    icon: str = Form(...),
    extension: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(generate_session),
):
    """ Upload a file to store as a recipe asset """
    file_name = slugify(name) + "." + extension
    asset_in = RecipeAsset(name=name, icon=icon, file_name=file_name)
    dest = Recipe(slug=recipe_slug).asset_dir.joinpath(file_name)

    with dest.open("wb") as buffer:
        copyfileobj(file.file, buffer)

    if not dest.is_file():
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    recipe: Recipe = db.recipes.get(session, recipe_slug)
    recipe.assets.append(asset_in)
    db.recipes.update(session, recipe_slug, recipe.dict())
    return asset_in
