from functools import cached_property
from shutil import copyfileobj
from zipfile import ZipFile

import sqlalchemy
from fastapi import BackgroundTasks, Depends, File, Form, HTTPException, status
from fastapi.datastructures import UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slugify import slugify
from starlette.responses import FileResponse

from mealie.core import exceptions
from mealie.core.dependencies import temporary_zip_path
from mealie.core.dependencies.dependencies import temporary_dir, validate_recipe_token
from mealie.core.security import create_recipe_slug_token
from mealie.pkgs import cache
from mealie.repos.repository_recipes import RepositoryRecipes
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.query import GetAll
from mealie.schema.recipe import Recipe, RecipeImageTypes, ScrapeRecipe
from mealie.schema.recipe.recipe import CreateRecipe, CreateRecipeByUrlBulk, RecipeSummary
from mealie.schema.recipe.recipe_asset import RecipeAsset
from mealie.schema.recipe.recipe_scraper import ScrapeRecipeTest
from mealie.schema.recipe.request_helpers import RecipeZipTokenResponse, UpdateImageResponse
from mealie.schema.response.responses import ErrorResponse
from mealie.services import urls
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.message_types import EventTypes
from mealie.services.recipe.recipe_data_service import RecipeDataService
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.recipe.template_service import TemplateService
from mealie.services.scraper.recipe_bulk_scraper import RecipeBulkScraperService
from mealie.services.scraper.scraped_extras import ScraperContext
from mealie.services.scraper.scraper import create_from_url
from mealie.services.scraper.scraper_strategies import RecipeScraperPackage


class BaseRecipeController(BaseUserController):
    @cached_property
    def repo(self) -> RepositoryRecipes:
        return self.repos.recipes.by_group(self.group_id)

    @cached_property
    def service(self) -> RecipeService:
        return RecipeService(self.repos, self.user, self.group)

    @cached_property
    def mixins(self):
        return HttpRepo[CreateRecipe, Recipe, Recipe](self.repo, self.deps.logger)


class RecipeGetAll(GetAll):
    load_food: bool = False


class FormatResponse(BaseModel):
    jjson: list[str] = Field(..., alias="json")
    zip: list[str]
    jinja2: list[str]


router_exports = UserAPIRouter(prefix="/recipes", tags=["Recipe: Exports"])


@controller(router_exports)
class RecipeExportController(BaseRecipeController):
    # ==================================================================================================================
    # Export Operations

    @router_exports.get("/exports", response_model=FormatResponse)
    def get_recipe_formats_and_templates(self):
        return TemplateService().templates

    @router_exports.post("/{slug}/exports", response_model=RecipeZipTokenResponse)
    def get_recipe_zip_token(self, slug: str):
        """Generates a recipe zip token to be used to download a recipe as a zip file"""
        return RecipeZipTokenResponse(token=create_recipe_slug_token(slug))

    @router_exports.get("/{slug}/exports", response_class=FileResponse)
    def get_recipe_as_format(self, slug: str, template_name: str, temp_dir=Depends(temporary_dir)):
        """
        ## Parameters
        `template_name`: The name of the template to use to use in the exports listed. Template type will automatically
        be set on the backend. Because of this, it's important that your templates have unique names. See available
        names and formats in the /api/recipes/exports endpoint.

        """
        recipe = self.mixins.get_one(slug)
        file = self.service.render_template(recipe, temp_dir, template_name)
        return FileResponse(file)

    @router_exports.get("/{slug}/exports/zip")
    def get_recipe_as_zip(self, slug: str, token: str, temp_path=Depends(temporary_zip_path)):
        """Get a Recipe and It's Original Image as a Zip File"""
        slug = validate_recipe_token(token)

        if slug != slug:
            raise HTTPException(status_code=400, detail="Invalid Slug")

        recipe: Recipe = self.mixins.get_one(slug)
        image_asset = recipe.image_dir.joinpath(RecipeImageTypes.original.value)
        with ZipFile(temp_path, "w") as myzip:
            myzip.writestr(f"{slug}.json", recipe.json())

            if image_asset.is_file():
                myzip.write(image_asset, arcname=image_asset.name)

        return FileResponse(temp_path, filename=f"{slug}.zip")


router = UserAPIRouter(prefix="/recipes", tags=["Recipe: CRUD"])


@controller(router)
class RecipeController(BaseRecipeController):
    event_bus: EventBusService = Depends(EventBusService)

    def handle_exceptions(self, ex: Exception) -> None:
        match type(ex):
            case exceptions.PermissionDenied:
                self.deps.logger.error("Permission Denied on recipe controller action")
                raise HTTPException(status_code=403, detail=ErrorResponse.respond(message="Permission Denied"))
            case exceptions.NoEntryFound:
                self.deps.logger.error("No Entry Found on recipe controller action")
                raise HTTPException(status_code=404, detail=ErrorResponse.respond(message="No Entry Found"))
            case sqlalchemy.exc.IntegrityError:
                self.deps.logger.error("SQL Integrity Error on recipe controller action")
                raise HTTPException(status_code=400, detail=ErrorResponse.respond(message="Recipe already exists"))

            case _:
                self.deps.logger.error("Unknown Error on recipe controller action")
                self.deps.logger.exception(ex)
                raise HTTPException(
                    status_code=500, detail=ErrorResponse.respond(message="Unknown Error", exception=str(ex))
                )

    # =======================================================================
    # URL Scraping Operations

    @router.post("/create-url", status_code=201, response_model=str)
    def parse_recipe_url(self, req: ScrapeRecipe):
        """Takes in a URL and attempts to scrape data and load it into the database"""
        recipe, extras = create_from_url(req.url)

        if req.include_tags:
            ctx = ScraperContext(self.user.id, self.group_id, self.repos)

            recipe.tags = extras.use_tags(ctx)  # type: ignore

        new_recipe = self.service.create_one(recipe)

        if new_recipe:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.recipe_created,
                msg=self.t(
                    "notifications.generic-created-with-url",
                    name=new_recipe.name,
                    url=urls.recipe_url(new_recipe.slug, self.deps.settings.BASE_URL),
                ),
            )

        return new_recipe.slug

    @router.post("/create-url/bulk", status_code=202)
    def parse_recipe_url_bulk(self, bulk: CreateRecipeByUrlBulk, bg_tasks: BackgroundTasks):
        """Takes in a URL and attempts to scrape data and load it into the database"""
        bulk_scraper = RecipeBulkScraperService(self.service, self.repos, self.group)
        report_id = bulk_scraper.get_report_id()
        bg_tasks.add_task(bulk_scraper.scrape, bulk)

        return {"reportId": report_id}

    @router.post("/test-scrape-url")
    def test_parse_recipe_url(self, url: ScrapeRecipeTest):
        # Debugger should produce the same result as the scraper sees before cleaning
        if scraped_data := RecipeScraperPackage(url.url).scrape_url():
            return scraped_data.schema.data

        return "recipe_scrapers was unable to scrape this URL"

    @router.post("/create-from-zip", status_code=201)
    def create_recipe_from_zip(self, temp_path=Depends(temporary_zip_path), archive: UploadFile = File(...)):
        """Create recipe from archive"""
        recipe = self.service.create_from_zip(archive, temp_path)
        return recipe.slug

    # ==================================================================================================================
    # CRUD Operations

    @router.get("", response_model=list[RecipeSummary])
    def get_all(self, q: RecipeGetAll = Depends(RecipeGetAll)):
        items = self.repo.summary(self.user.group_id, start=q.start, limit=q.limit, load_foods=q.load_food)

        new_items = []
        for item in items:
            # Pydantic/FastAPI can't seem to serialize the ingredient field on thier own.
            new_item = item.__dict__

            if q.load_food:
                new_item["recipe_ingredient"] = [x.__dict__ for x in item.recipe_ingredient]

            new_items.append(new_item)

        json_compatible_item_data = jsonable_encoder(RecipeSummary.construct(**x) for x in new_items)

        # Response is returned directly, to avoid validation and improve performance
        return JSONResponse(content=json_compatible_item_data)

    @router.get("/{slug}", response_model=Recipe)
    def get_one(self, slug: str):
        """Takes in a recipe slug, returns all data for a recipe"""
        return self.mixins.get_one(slug)

    @router.post("", status_code=201, response_model=str)
    def create_one(self, data: CreateRecipe) -> str | None:
        """Takes in a JSON string and loads data into the database as a new entry"""
        try:
            return self.service.create_one(data).slug
        except Exception as e:
            self.handle_exceptions(e)
            return None

    @router.put("/{slug}")
    def update_one(self, slug: str, data: Recipe):
        """Updates a recipe by existing slug and data."""
        try:
            data = self.service.update_one(slug, data)
        except Exception as e:
            self.handle_exceptions(e)

        if data:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.recipe_updated,
                msg=self.t(
                    "notifications.generic-updated-with-url",
                    name=data.name,
                    url=urls.recipe_url(data.slug, self.deps.settings.BASE_URL),
                ),
            )

        return data

    @router.patch("/{slug}")
    def patch_one(self, slug: str, data: Recipe):
        """Updates a recipe by existing slug and data."""
        try:
            data = self.service.patch_one(slug, data)
        except Exception as e:
            self.handle_exceptions(e)
        return data

    @router.delete("/{slug}")
    def delete_one(self, slug: str):
        """Deletes a recipe by slug"""
        try:
            data = self.service.delete_one(slug)
        except Exception as e:
            self.handle_exceptions(e)

        if data:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.recipe_deleted,
                msg=self.t("notifications.generic-deleted", name=data.name),
            )

        return data

    # ==================================================================================================================
    # Image and Assets

    @router.post("/{slug}/image", tags=["Recipe: Images and Assets"])
    def scrape_image_url(self, slug: str, url: ScrapeRecipe):
        recipe = self.mixins.get_one(slug)
        data_service = RecipeDataService(recipe.id)
        data_service.scrape_image(url.url)

        recipe.image = cache.cache_key.new_key()
        self.service.update_one(recipe.slug, recipe)

    @router.put("/{slug}/image", response_model=UpdateImageResponse, tags=["Recipe: Images and Assets"])
    def update_recipe_image(self, slug: str, image: bytes = File(...), extension: str = Form(...)):
        recipe = self.mixins.get_one(slug)
        data_service = RecipeDataService(recipe.id)
        data_service.write_image(image, extension)

        new_version = self.repo.update_image(slug, extension)
        return UpdateImageResponse(image=new_version)

    @router.post("/{slug}/assets", response_model=RecipeAsset, tags=["Recipe: Images and Assets"])
    def upload_recipe_asset(
        self,
        slug: str,
        name: str = Form(...),
        icon: str = Form(...),
        extension: str = Form(...),
        file: UploadFile = File(...),
    ):
        """Upload a file to store as a recipe asset"""
        file_name = f"{slugify(name)}.{extension}"
        asset_in = RecipeAsset(name=name, icon=icon, file_name=file_name)

        recipe = self.mixins.get_one(slug)

        dest = recipe.asset_dir / file_name

        with dest.open("wb") as buffer:
            copyfileobj(file.file, buffer)

        if not dest.is_file():
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

        recipe = self.mixins.get_one(slug)
        recipe.assets.append(asset_in)

        self.mixins.update_one(recipe, slug)

        return asset_in
