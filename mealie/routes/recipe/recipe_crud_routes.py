from zipfile import ZipFile

from fastapi import Depends, File
from fastapi.datastructures import UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse

from mealie.core.dependencies import temporary_zip_path
from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe import CreateRecipeByUrl, Recipe, RecipeImageTypes
from mealie.schema.recipe.recipe import CreateRecipe, CreateRecipeByUrlBulk, RecipeSummary
from mealie.schema.server.tasks import ServerTaskNames
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.scraper.scraper import create_from_url, scrape_from_url
from mealie.services.server_tasks.background_executory import BackgroundExecutor

user_router = UserAPIRouter()
logger = get_logger()


@user_router.get("", response_model=list[RecipeSummary])
async def get_all(start=0, limit=None, service: RecipeService = Depends(RecipeService.private)):
    json_compatible_item_data = jsonable_encoder(service.get_all(start, limit))
    return JSONResponse(content=json_compatible_item_data)


@user_router.post("", status_code=201, response_model=str)
def create_from_name(data: CreateRecipe, recipe_service: RecipeService = Depends(RecipeService.private)) -> str:
    """ Takes in a JSON string and loads data into the database as a new entry"""
    return recipe_service.create_one(data).slug


@user_router.post("/create-url", status_code=201, response_model=str)
def parse_recipe_url(url: CreateRecipeByUrl, recipe_service: RecipeService = Depends(RecipeService.private)):
    """ Takes in a URL and attempts to scrape data and load it into the database """
    recipe = create_from_url(url.url)
    return recipe_service.create_one(recipe).slug


@user_router.post("/create-url/bulk", status_code=202)
def parse_recipe_url_bulk(
    bulk: CreateRecipeByUrlBulk,
    recipe_service: RecipeService = Depends(RecipeService.private),
    bg_service: BackgroundExecutor = Depends(BackgroundExecutor.private),
):
    """ Takes in a URL and attempts to scrape data and load it into the database """

    def bulk_import_func(task_id: int, session: Session) -> None:
        database = get_database(session)
        task = database.server_tasks.get_one(task_id)

        task.append_log("test task has started")

        for b in bulk.imports:
            try:
                recipe = create_from_url(b.url)

                if b.tags:
                    recipe.tags = b.tags

                if b.categories:
                    recipe.recipe_category = b.categories

                recipe_service.create_one(recipe)
                task.append_log(f"INFO: Created recipe from url: {b.url}")
            except Exception as e:
                task.append_log(f"Error: Failed to create recipe from url: {b.url}")
                task.append_log(f"Error: {e}")
                logger.error(f"Failed to create recipe from url: {b.url}")
                logger.error(e)
            database.server_tasks.update(task.id, task)

        task.set_finished()
        database.server_tasks.update(task.id, task)

    bg_service.dispatch(ServerTaskNames.bulk_recipe_import, bulk_import_func)

    return {"details": "task has been started"}


@user_router.post("/test-scrape-url")
def test_parse_recipe_url(url: CreateRecipeByUrl):
    # Debugger should produce the same result as the scraper sees before cleaning
    scraped_data = scrape_from_url(url.url)
    if scraped_data:
        return scraped_data.schema.data
    return "recipe_scrapers was unable to scrape this URL"


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
