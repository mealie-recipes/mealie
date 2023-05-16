from functools import cached_property
from shutil import copyfileobj
from zipfile import ZipFile

import orjson
import sqlalchemy
from fastapi import BackgroundTasks, Depends, File, Form, HTTPException, Path, Query, Request, status
from fastapi.datastructures import UploadFile
from fastapi.responses import JSONResponse
from pydantic import UUID4, BaseModel, Field
from slugify import slugify
from starlette.responses import FileResponse

from mealie.core import exceptions
from mealie.core.dependencies import temporary_zip_path
from mealie.core.dependencies.dependencies import temporary_dir, validate_recipe_token
from mealie.core.security import create_recipe_slug_token
from mealie.db.models.group.cookbook import CookBook
from mealie.pkgs import cache
from mealie.repos.repository_generic import RepositoryGeneric
from mealie.repos.repository_recipes import RepositoryRecipes
from mealie.routes._base import BaseCrudController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute, UserAPIRouter
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.make_dependable import make_dependable
from mealie.schema.recipe import Recipe, RecipeImageTypes, ScrapeRecipe
from mealie.schema.recipe.recipe import CreateRecipe, CreateRecipeByUrlBulk, RecipeLastMade, RecipeSummary
from mealie.schema.recipe.recipe_asset import RecipeAsset
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_scraper import ScrapeRecipeTest
from mealie.schema.recipe.recipe_settings import RecipeSettings
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.schema.recipe.request_helpers import RecipeDuplicate, RecipeZipTokenResponse, UpdateImageResponse
from mealie.schema.response import PaginationBase, PaginationQuery
from mealie.schema.response.pagination import RecipeSearchQuery
from mealie.schema.response.responses import ErrorResponse
from mealie.services import urls
from mealie.services.event_bus_service.event_types import (
    EventOperation,
    EventRecipeBulkReportData,
    EventRecipeData,
    EventTypes,
)
from mealie.services.recipe.recipe_data_service import InvalidDomainError, NotAnImageError, RecipeDataService
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.recipe.template_service import TemplateService
from mealie.services.scraper.recipe_bulk_scraper import RecipeBulkScraperService
from mealie.services.scraper.scraped_extras import ScraperContext
from mealie.services.scraper.scraper import create_from_url
from mealie.services.scraper.scraper_strategies import ForceTimeoutException, RecipeScraperPackage


class JSONBytes(JSONResponse):
    """
    JSONBytes overrides the render method to return the bytes instead of a string.
    You can use this when you want to use orjson and bypass the jsonable_encoder
    """

    media_type = "application/json"

    def render(self, content: bytes) -> bytes:
        return content


class BaseRecipeController(BaseCrudController):
    @cached_property
    def repo(self) -> RepositoryRecipes:
        return self.repos.recipes.by_group(self.group_id)

    @cached_property
    def cookbooks_repo(self) -> RepositoryGeneric[ReadCookBook, CookBook]:
        return self.repos.cookbooks.by_group(self.group_id)

    @cached_property
    def service(self) -> RecipeService:
        return RecipeService(self.repos, self.user, self.group)

    @cached_property
    def mixins(self):
        return HttpRepo[CreateRecipe, Recipe, Recipe](self.repo, self.logger)


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


router = UserAPIRouter(prefix="/recipes", tags=["Recipe: CRUD"], route_class=MealieCrudRoute)


@controller(router)
class RecipeController(BaseRecipeController):
    def handle_exceptions(self, ex: Exception) -> None:
        thrownType = type(ex)

        if thrownType == exceptions.PermissionDenied:
            self.logger.error("Permission Denied on recipe controller action")
            raise HTTPException(status_code=403, detail=ErrorResponse.respond(message="Permission Denied"))
        elif thrownType == exceptions.NoEntryFound:
            self.logger.error("No Entry Found on recipe controller action")
            raise HTTPException(status_code=404, detail=ErrorResponse.respond(message="No Entry Found"))
        elif thrownType == sqlalchemy.exc.IntegrityError:
            self.logger.error("SQL Integrity Error on recipe controller action")
            raise HTTPException(status_code=400, detail=ErrorResponse.respond(message="Recipe already exists"))
        else:
            self.logger.error("Unknown Error on recipe controller action")
            self.logger.exception(ex)
            raise HTTPException(
                status_code=500, detail=ErrorResponse.respond(message="Unknown Error", exception=ex.__class__.__name__)
            )

    # =======================================================================
    # URL Scraping Operations

    @router.post("/create-url", status_code=201, response_model=str)
    async def parse_recipe_url(self, req: ScrapeRecipe):
        """Takes in a URL and attempts to scrape data and load it into the database"""
        try:
            recipe, extras = await create_from_url(req.url)
        except ForceTimeoutException as e:
            raise HTTPException(
                status_code=408, detail=ErrorResponse.respond(message="Recipe Scraping Timed Out")
            ) from e

        if req.include_tags:
            ctx = ScraperContext(self.user.id, self.group_id, self.repos)

            recipe.tags = extras.use_tags(ctx)  # type: ignore

        new_recipe = self.service.create_one(recipe)

        if new_recipe:
            self.publish_event(
                event_type=EventTypes.recipe_created,
                document_data=EventRecipeData(operation=EventOperation.create, recipe_slug=new_recipe.slug),
                message=self.t(
                    "notifications.generic-created-with-url",
                    name=new_recipe.name,
                    url=urls.recipe_url(new_recipe.slug, self.settings.BASE_URL),
                ),
            )

        return new_recipe.slug

    @router.post("/create-url/bulk", status_code=202)
    def parse_recipe_url_bulk(self, bulk: CreateRecipeByUrlBulk, bg_tasks: BackgroundTasks):
        """Takes in a URL and attempts to scrape data and load it into the database"""
        bulk_scraper = RecipeBulkScraperService(self.service, self.repos, self.group)
        report_id = bulk_scraper.get_report_id()
        bg_tasks.add_task(bulk_scraper.scrape, bulk)

        self.publish_event(
            event_type=EventTypes.recipe_created,
            document_data=EventRecipeBulkReportData(operation=EventOperation.create, report_id=report_id),
        )

        return {"reportId": report_id}

    @router.post("/test-scrape-url")
    async def test_parse_recipe_url(self, url: ScrapeRecipeTest):
        # Debugger should produce the same result as the scraper sees before cleaning
        try:
            if scraped_data := await RecipeScraperPackage(url.url).scrape_url():
                return scraped_data.schema.data
        except ForceTimeoutException as e:
            raise HTTPException(
                status_code=408, detail=ErrorResponse.respond(message="Recipe Scraping Timed Out")
            ) from e

        return "recipe_scrapers was unable to scrape this URL"

    @router.post("/create-from-zip", status_code=201)
    def create_recipe_from_zip(self, temp_path=Depends(temporary_zip_path), archive: UploadFile = File(...)):
        """Create recipe from archive"""
        recipe = self.service.create_from_zip(archive, temp_path)
        self.publish_event(
            event_type=EventTypes.recipe_created,
            document_data=EventRecipeData(operation=EventOperation.create, recipe_slug=recipe.slug),
        )

        return recipe.slug

    # ==================================================================================================================
    # CRUD Operations

    @router.get("", response_model=PaginationBase[RecipeSummary])
    def get_all(
        self,
        request: Request,
        q: PaginationQuery = Depends(make_dependable(PaginationQuery)),
        search_query: RecipeSearchQuery = Depends(make_dependable(RecipeSearchQuery)),
        categories: list[UUID4 | str] | None = Query(None),
        tags: list[UUID4 | str] | None = Query(None),
        tools: list[UUID4 | str] | None = Query(None),
        foods: list[UUID4 | str] | None = Query(None),
    ):
        cookbook_data: ReadCookBook | None = None
        if search_query.cookbook:
            cb_match_attr = "slug" if isinstance(search_query.cookbook, str) else "id"
            cookbook_data = self.cookbooks_repo.get_one(search_query.cookbook, cb_match_attr)

            if search_query.cookbook is None:
                raise HTTPException(status_code=404, detail="cookbook not found")

        pagination_response = self.repo.page_all(
            pagination=q,
            cookbook=cookbook_data,
            categories=categories,
            tags=tags,
            tools=tools,
            foods=foods,
            require_all_categories=search_query.require_all_categories,
            require_all_tags=search_query.require_all_tags,
            require_all_tools=search_query.require_all_tools,
            require_all_foods=search_query.require_all_foods,
            search=search_query.search,
        )

        # merge default pagination with the request's query params
        query_params = q.dict() | {**request.query_params}
        pagination_response.set_pagination_guides(
            router.url_path_for("get_all"),
            {k: v for k, v in query_params.items() if v is not None},
        )

        json_compatible_response = orjson.dumps(pagination_response.dict(by_alias=True))

        # Response is returned directly, to avoid validation and improve performance
        return JSONBytes(content=json_compatible_response)

    @router.get("/{slug}", response_model=Recipe)
    def get_one(self, slug: str = Path(..., description="A recipe's slug or id")):
        """Takes in a recipe's slug or id and returns all data for a recipe"""
        try:
            recipe = self.service.get_one_by_slug_or_id(slug)
        except Exception as e:
            self.handle_exceptions(e)
            return None

        return recipe

    @router.post("", status_code=201, response_model=str)
    def create_one(self, data: CreateRecipe) -> str | None:
        """Takes in a JSON string and loads data into the database as a new entry"""
        try:
            new_recipe = self.service.create_one(data)
        except Exception as e:
            self.handle_exceptions(e)
            return None

        if new_recipe:
            self.publish_event(
                event_type=EventTypes.recipe_created,
                document_data=EventRecipeData(operation=EventOperation.create, recipe_slug=new_recipe.slug),
                message=self.t(
                    "notifications.generic-created-with-url",
                    name=new_recipe.name,
                    url=urls.recipe_url(new_recipe.slug, self.settings.BASE_URL),
                ),
            )

        return new_recipe.slug

    @router.post("/{slug}/duplicate", status_code=201, response_model=Recipe)
    def duplicate_one(self, slug: str, req: RecipeDuplicate) -> Recipe:
        """Duplicates a recipe with a new custom name if given"""
        try:
            new_recipe = self.service.duplicate_one(slug, req)
        except Exception as e:
            self.handle_exceptions(e)

        if new_recipe:
            self.publish_event(
                event_type=EventTypes.recipe_created,
                document_data=EventRecipeData(operation=EventOperation.create, recipe_slug=new_recipe.slug),
                message=self.t(
                    "notifications.generic-duplicated",
                    name=new_recipe.name,
                ),
            )

        return new_recipe

    @router.put("/{slug}")
    def update_one(self, slug: str, data: Recipe):
        """Updates a recipe by existing slug and data."""
        try:
            recipe = self.service.update_one(slug, data)
        except Exception as e:
            self.handle_exceptions(e)

        if recipe:
            self.publish_event(
                event_type=EventTypes.recipe_updated,
                document_data=EventRecipeData(operation=EventOperation.update, recipe_slug=recipe.slug),
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=recipe.name,
                    url=urls.recipe_url(recipe.slug, self.settings.BASE_URL),
                ),
            )

        return recipe

    @router.patch("/{slug}")
    def patch_one(self, slug: str, data: Recipe):
        """Updates a recipe by existing slug and data."""
        try:
            recipe = self.service.patch_one(slug, data)
        except Exception as e:
            self.handle_exceptions(e)

        if recipe:
            self.publish_event(
                event_type=EventTypes.recipe_updated,
                document_data=EventRecipeData(operation=EventOperation.update, recipe_slug=recipe.slug),
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=recipe.name,
                    url=urls.recipe_url(recipe.slug, self.settings.BASE_URL),
                ),
            )

        return recipe

    @router.patch("/{slug}/last-made")
    def update_last_made(self, slug: str, data: RecipeLastMade):
        """Update a recipe's last made timestamp"""

        try:
            recipe = self.service.update_last_made(slug, data.timestamp)
        except Exception as e:
            self.handle_exceptions(e)

        if recipe:
            self.publish_event(
                event_type=EventTypes.recipe_updated,
                document_data=EventRecipeData(operation=EventOperation.update, recipe_slug=recipe.slug),
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=recipe.name,
                    url=urls.recipe_url(recipe.slug, self.settings.BASE_URL),
                ),
            )

        return recipe

    @router.delete("/{slug}")
    def delete_one(self, slug: str):
        """Deletes a recipe by slug"""
        try:
            recipe = self.service.delete_one(slug)
        except Exception as e:
            self.handle_exceptions(e)

        if recipe:
            self.publish_event(
                event_type=EventTypes.recipe_deleted,
                document_data=EventRecipeData(operation=EventOperation.delete, recipe_slug=recipe.slug),
                message=self.t("notifications.generic-deleted", name=recipe.name),
            )

        return recipe

    # ==================================================================================================================
    # Image and Assets

    @router.post("/{slug}/image", tags=["Recipe: Images and Assets"])
    async def scrape_image_url(self, slug: str, url: ScrapeRecipe):
        recipe = self.mixins.get_one(slug)
        data_service = RecipeDataService(recipe.id)

        try:
            await data_service.scrape_image(url.url)
        except NotAnImageError as e:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse.respond("Url is not an image"),
            ) from e
        except InvalidDomainError as e:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse.respond("Url is not from an allowed domain"),
            ) from e

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
        if "." in extension:
            extension = extension.split(".")[-1]

        file_slug = slugify(name)
        if not extension or not file_slug:
            raise HTTPException(status_code=400, detail="Missing required fields")

        file_name = f"{file_slug}.{extension}"
        asset_in = RecipeAsset(name=name, icon=icon, file_name=file_name)

        recipe = self.mixins.get_one(slug)

        dest = recipe.asset_dir / file_name

        # Ensure path is relative to the recipe's asset directory
        if dest.absolute().parent != recipe.asset_dir:
            raise HTTPException(
                status_code=400,
                detail=f"File name {file_name} or extension {extension} not valid",
            )

        with dest.open("wb") as buffer:
            copyfileobj(file.file, buffer)

        if not dest.is_file():
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

        recipe = self.mixins.get_one(slug)
        recipe.assets.append(asset_in)

        self.mixins.update_one(recipe, slug)

        return asset_in

    # ==================================================================================================================
    # OCR
    @router.post("/create-ocr", status_code=201, response_model=str)
    def create_recipe_ocr(
        self, extension: str = Form(...), file: UploadFile = File(...), makefilerecipeimage: bool = Form(...)
    ):
        """Takes an image and creates a recipe based on the image"""
        slug = self.service.create_one(
            Recipe(
                name="New OCR Recipe",
                recipe_ingredient=[RecipeIngredient(note="", title=None, unit=None, food=None, original_text=None)],
                recipe_instructions=[RecipeStep(text="")],
                is_ocr_recipe=True,
                settings=RecipeSettings(show_assets=True),
                id=None,
                image=None,
                recipe_yield=None,
                rating=None,
                orgURL=None,
                date_added=None,
                date_updated=None,
                created_at=None,
                update_at=None,
                nutrition=None,
            )
        ).slug
        RecipeController.upload_recipe_asset(self, slug, "Original recipe image", "", extension, file)
        if makefilerecipeimage:
            # Get the pointer to the beginning of the file to read it once more
            file.file.seek(0)
            self.update_recipe_image(slug, file.file.read(), extension)

        return slug
