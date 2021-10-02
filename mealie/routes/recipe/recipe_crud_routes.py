from zipfile import ZipFile

from fastapi import Depends, File
from fastapi.datastructures import UploadFile
from scrape_schema_recipe import scrape_url
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse

from mealie.core.dependencies import temporary_zip_path
from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe import CreateRecipeByURL, Recipe, RecipeImageTypes
from mealie.schema.recipe.recipe import CreateRecipe, RecipeSummary
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.scraper.scraper import create_from_url

user_router = UserAPIRouter()
logger = get_logger()


@user_router.get("", response_model=list[RecipeSummary])
async def get_all(start=0, limit=None, service: RecipeService = Depends(RecipeService.private)):
    return service.get_all(start, limit)


@user_router.post("", status_code=201, response_model=str)
def create_from_name(data: CreateRecipe, recipe_service: RecipeService = Depends(RecipeService.private)) -> str:
    """ Takes in a JSON string and loads data into the database as a new entry"""
    return recipe_service.create_one(data).slug


@user_router.post("/create-url", status_code=201, response_model=str)
def parse_recipe_url(url: CreateRecipeByURL, recipe_service: RecipeService = Depends(RecipeService.private)):
    """ Takes in a URL and attempts to scrape data and load it into the database """

    recipe = create_from_url(url.url)
    return recipe_service.create_one(recipe).slug


@user_router.post("/test-scrape-url")
def test_parse_recipe_url(url: CreateRecipeByURL):
    # TODO: Replace with more current implementation of testing schema
    return scrape_url(url.url)


@user_router.post("/create-from-zip", status_code=201)
async def create_recipe_from_zip(
    recipe_service: RecipeService = Depends(RecipeService.private),
    temp_path=Depends(temporary_zip_path),
    archive: UploadFile = File(...),
):
    """ Create recipe from archive """
    recipe = recipe_service.create_from_zip(archive, temp_path)
    return recipe.slug


@user_router.get("/{slug}", response_model=Recipe)
def get_recipe(recipe_service: RecipeService = Depends(RecipeService.read_existing)):
    """ Takes in a recipe slug, returns all data for a recipe """
    return recipe_service.item


@user_router.get("/{slug}/zip")
async def get_recipe_as_zip(
    slug: str, session: Session = Depends(generate_session), temp_path=Depends(temporary_zip_path)
):
    """ Get a Recipe and It's Original Image as a Zip File """
    db = get_database(session)

    recipe: Recipe = db.recipes.get(slug)

    image_asset = recipe.image_dir.joinpath(RecipeImageTypes.original.value)

    with ZipFile(temp_path, "w") as myzip:
        myzip.writestr(f"{slug}.json", recipe.json())

        if image_asset.is_file():
            myzip.write(image_asset, arcname=image_asset.name)

    return FileResponse(temp_path, filename=f"{slug}.zip")


@user_router.put("/{slug}")
def update_recipe(data: Recipe, recipe_service: RecipeService = Depends(RecipeService.write_existing)):
    """ Updates a recipe by existing slug and data. """
    return recipe_service.update_one(data)


@user_router.patch("/{slug}")
def patch_recipe(data: Recipe, recipe_service: RecipeService = Depends(RecipeService.write_existing)):
    """ Updates a recipe by existing slug and data. """
    return recipe_service.patch_one(data)


@user_router.delete("/{slug}")
def delete_recipe(recipe_service: RecipeService = Depends(RecipeService.write_existing)):
    """ Deletes a recipe by slug """
    return recipe_service.delete_one()
