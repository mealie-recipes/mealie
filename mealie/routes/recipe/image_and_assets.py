from shutil import copyfileobj

from fastapi import Depends, File, Form, HTTPException, status
from fastapi.datastructures import UploadFile
from slugify import slugify
from sqlalchemy.orm.session import Session

from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe import CreateRecipeByUrl, Recipe, RecipeAsset
from mealie.services.image.image import scrape_image, write_image

user_router = UserAPIRouter()


@user_router.post("/{slug}/image")
def scrape_image_url(slug: str, url: CreateRecipeByUrl):
    """ Removes an existing image and replaces it with the incoming file. """

    scrape_image(url.url, slug)


@user_router.put("/{slug}/image")
def update_recipe_image(
    slug: str,
    image: bytes = File(...),
    extension: str = Form(...),
    session: Session = Depends(generate_session),
):
    """ Removes an existing image and replaces it with the incoming file. """
    db = get_database(session)
    write_image(slug, image, extension)
    new_version = db.recipes.update_image(slug, extension)

    return {"image": new_version}


@user_router.post("/{slug}/assets", response_model=RecipeAsset)
def upload_recipe_asset(
    slug: str,
    name: str = Form(...),
    icon: str = Form(...),
    extension: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(generate_session),
):
    """ Upload a file to store as a recipe asset """
    file_name = slugify(name) + "." + extension
    asset_in = RecipeAsset(name=name, icon=icon, file_name=file_name)
    dest = Recipe(slug=slug).asset_dir.joinpath(file_name)

    with dest.open("wb") as buffer:
        copyfileobj(file.file, buffer)

    if not dest.is_file():
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    db = get_database(session)

    recipe: Recipe = db.recipes.get(slug)
    recipe.assets.append(asset_in)
    db.recipes.update(slug, recipe.dict())
    return asset_in
