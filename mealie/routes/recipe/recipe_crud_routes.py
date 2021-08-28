import json
import shutil
from zipfile import ZipFile

from fastapi import APIRouter, BackgroundTasks, Depends, File
from fastapi.datastructures import UploadFile
from mealie.core.config import settings
from mealie.core.root_logger import get_logger
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user, temporary_zip_path
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe import CreateRecipeByURL, Recipe, RecipeImageTypes
from mealie.schema.recipe.recipe import CreateRecipe
from mealie.schema.user import UserInDB
from mealie.services.events import create_recipe_event
from mealie.services.image.image import write_image
from mealie.services.recipe.media import check_assets
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.scraper.scraper import create_from_url
from scrape_schema_recipe import scrape_url
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse

user_router = UserAPIRouter()
public_router = APIRouter()
logger = get_logger()


@user_router.post("", status_code=201, response_model=str)
def create_from_name(data: CreateRecipe, recipe_service: RecipeService = Depends(RecipeService.base)) -> str:
    """ Takes in a JSON string and loads data into the database as a new entry"""
    return recipe_service.create_recipe(data).slug


@user_router.post("/test-scrape-url")
def test_parse_recipe_url(url: CreateRecipeByURL):
    return scrape_url(url.url)


@user_router.post("/create-url", status_code=201, response_model=str)
def parse_recipe_url(
    background_tasks: BackgroundTasks,
    url: CreateRecipeByURL,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Takes in a URL and attempts to scrape data and load it into the database """

    recipe = create_from_url(url.url)
    recipe: Recipe = db.recipes.create(session, recipe.dict())

    background_tasks.add_task(
        create_recipe_event,
        "Recipe Created (URL)",
        f"'{recipe.name}' by {current_user.full_name} \n {settings.BASE_URL}/recipe/{recipe.slug}",
        session=session,
        attachment=recipe.image_dir.joinpath("min-original.webp"),
    )

    return recipe.slug


@public_router.get("/{slug}", response_model=Recipe)
def get_recipe(recipe_service: RecipeService = Depends(RecipeService.read_existing)):
    """ Takes in a recipe slug, returns all data for a recipe """
    return recipe_service.recipe


@user_router.post("/create-from-zip")
async def create_recipe_from_zip(
    session: Session = Depends(generate_session),
    temp_path=Depends(temporary_zip_path),
    archive: UploadFile = File(...),
):
    """ Create recipe from archive """

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(archive.file, buffer)

    recipe_dict = None
    recipe_image = None

    with ZipFile(temp_path) as myzip:
        for file in myzip.namelist():
            if file.endswith(".json"):
                with myzip.open(file) as myfile:
                    recipe_dict = json.loads(myfile.read())
            elif file.endswith(".webp"):
                with myzip.open(file) as myfile:
                    recipe_image = myfile.read()

    recipe: Recipe = db.recipes.create(session, Recipe(**recipe_dict))

    write_image(recipe.slug, recipe_image, "webp")

    return recipe


@public_router.get("/{recipe_slug}/zip")
async def get_recipe_as_zip(
    recipe_slug: str, session: Session = Depends(generate_session), temp_path=Depends(temporary_zip_path)
):
    """ Get a Recipe and It's Original Image as a Zip File """
    recipe: Recipe = db.recipes.get(session, recipe_slug)

    image_asset = recipe.image_dir.joinpath(RecipeImageTypes.original.value)

    with ZipFile(temp_path, "w") as myzip:
        myzip.writestr(f"{recipe_slug}.json", recipe.json())

        if image_asset.is_file():
            myzip.write(image_asset, arcname=image_asset.name)

    return FileResponse(temp_path, filename=f"{recipe_slug}.zip")


@user_router.put("/{recipe_slug}")
def update_recipe(
    recipe_slug: str,
    data: Recipe,
    session: Session = Depends(generate_session),
):
    """ Updates a recipe by existing slug and data. """

    recipe: Recipe = db.recipes.update(session, recipe_slug, data.dict())

    check_assets(original_slug=recipe_slug, recipe=recipe)

    return recipe


@user_router.patch("/{recipe_slug}")
def patch_recipe(
    recipe_slug: str,
    data: Recipe,
    session: Session = Depends(generate_session),
):
    """ Updates a recipe by existing slug and data. """

    recipe: Recipe = db.recipes.patch(
        session, recipe_slug, new_data=data.dict(exclude_unset=True, exclude_defaults=True)
    )

    check_assets(original_slug=recipe_slug, recipe=recipe)

    return recipe


@user_router.delete("/{slug}")
def delete_recipe(recipe_service: RecipeService = Depends(RecipeService.write_existing)):
    """ Deletes a recipe by slug """
    return recipe_service.delete_recipe()
