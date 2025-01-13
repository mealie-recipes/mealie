from collections import defaultdict
from shutil import copyfileobj
from uuid import UUID

import orjson
import sqlalchemy
from fastapi import (
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    Request,
    status,
)
from fastapi.datastructures import UploadFile
from pydantic import UUID4
from slugify import slugify

from mealie.core import exceptions
from mealie.core.dependencies import (
    get_temporary_zip_path,
)
from mealie.pkgs import cache
from mealie.repos.all_repositories import get_repositories
from mealie.routes._base import controller
from mealie.routes._base.routers import MealieCrudRoute, UserAPIRouter
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.make_dependable import make_dependable
from mealie.schema.recipe import Recipe, ScrapeRecipe, ScrapeRecipeData
from mealie.schema.recipe.recipe import (
    CreateRecipe,
    CreateRecipeByUrlBulk,
    RecipeLastMade,
    RecipeSummary,
)
from mealie.schema.recipe.recipe_asset import RecipeAsset
from mealie.schema.recipe.recipe_scraper import ScrapeRecipeTest
from mealie.schema.recipe.recipe_suggestion import RecipeSuggestionQuery, RecipeSuggestionResponse
from mealie.schema.recipe.request_helpers import (
    RecipeDuplicate,
    UpdateImageResponse,
)
from mealie.schema.response import PaginationBase, PaginationQuery
from mealie.schema.response.pagination import RecipeSearchQuery
from mealie.schema.response.responses import ErrorResponse
from mealie.services import urls
from mealie.services.event_bus_service.event_types import (
    EventOperation,
    EventRecipeBulkData,
    EventRecipeBulkReportData,
    EventRecipeData,
    EventTypes,
)
from mealie.services.recipe.recipe_data_service import (
    InvalidDomainError,
    NotAnImageError,
    RecipeDataService,
)
from mealie.services.scraper.recipe_bulk_scraper import RecipeBulkScraperService
from mealie.services.scraper.scraped_extras import ScraperContext
from mealie.services.scraper.scraper import create_from_html
from mealie.services.scraper.scraper_strategies import (
    ForceTimeoutException,
    RecipeScraperOpenAI,
    RecipeScraperPackage,
)

from ._base import BaseRecipeController, JSONBytes

router = UserAPIRouter(prefix="/recipes", route_class=MealieCrudRoute)


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

    @router.post("/test-scrape-url")
    async def test_parse_recipe_url(self, data: ScrapeRecipeTest):
        # Debugger should produce the same result as the scraper sees before cleaning
        ScraperClass = RecipeScraperOpenAI if data.use_openai else RecipeScraperPackage
        try:
            if scraped_data := await ScraperClass(data.url, self.translator).scrape_url():
                return scraped_data.schema.data
        except ForceTimeoutException as e:
            raise HTTPException(
                status_code=408, detail=ErrorResponse.respond(message="Recipe Scraping Timed Out")
            ) from e

        return "recipe_scrapers was unable to scrape this URL"

    @router.post("/create/html-or-json", status_code=201)
    async def create_recipe_from_html_or_json(self, req: ScrapeRecipeData):
        """Takes in raw HTML or a https://schema.org/Recipe object as a JSON string and parses it like a URL"""

        if req.data.startswith("{"):
            req.data = RecipeScraperPackage.ld_json_to_html(req.data)

        return await self._create_recipe_from_web(req)

    @router.post("/create/url", status_code=201, response_model=str)
    async def parse_recipe_url(self, req: ScrapeRecipe):
        """Takes in a URL and attempts to scrape data and load it into the database"""

        return await self._create_recipe_from_web(req)

    async def _create_recipe_from_web(self, req: ScrapeRecipe | ScrapeRecipeData):
        if isinstance(req, ScrapeRecipeData):
            html = req.data
            url = ""
        else:
            html = None
            url = req.url

        try:
            recipe, extras = await create_from_html(url, self.translator, html)
        except ForceTimeoutException as e:
            raise HTTPException(
                status_code=408, detail=ErrorResponse.respond(message="Recipe Scraping Timed Out")
            ) from e

        if req.include_tags:
            ctx = ScraperContext(self.repos)

            recipe.tags = extras.use_tags(ctx)  # type: ignore

        new_recipe = self.service.create_one(recipe)

        if new_recipe:
            self.publish_event(
                event_type=EventTypes.recipe_created,
                document_data=EventRecipeData(operation=EventOperation.create, recipe_slug=new_recipe.slug),
                group_id=new_recipe.group_id,
                household_id=new_recipe.household_id,
                message=self.t(
                    "notifications.generic-created-with-url",
                    name=new_recipe.name,
                    url=urls.recipe_url(self.group.slug, new_recipe.slug, self.settings.BASE_URL),
                ),
            )

        return new_recipe.slug

    @router.post("/create/url/bulk", status_code=202)
    def parse_recipe_url_bulk(self, bulk: CreateRecipeByUrlBulk, bg_tasks: BackgroundTasks):
        """Takes in a URL and attempts to scrape data and load it into the database"""
        bulk_scraper = RecipeBulkScraperService(self.service, self.repos, self.group, self.translator)
        report_id = bulk_scraper.get_report_id()
        bg_tasks.add_task(bulk_scraper.scrape, bulk)

        self.publish_event(
            event_type=EventTypes.recipe_created,
            document_data=EventRecipeBulkReportData(operation=EventOperation.create, report_id=report_id),
            group_id=self.group_id,
            household_id=self.household_id,
        )

        return {"reportId": report_id}

    # ==================================================================================================================
    # Other Create Operations

    @router.post("/create/zip", status_code=201)
    def create_recipe_from_zip(self, archive: UploadFile = File(...)):
        """Create recipe from archive"""
        with get_temporary_zip_path() as temp_path:
            recipe = self.service.create_from_zip(archive, temp_path)
            self.publish_event(
                event_type=EventTypes.recipe_created,
                document_data=EventRecipeData(operation=EventOperation.create, recipe_slug=recipe.slug),
                group_id=recipe.group_id,
                household_id=recipe.household_id,
            )

        return recipe.slug

    @router.post("/create/image", status_code=201)
    async def create_recipe_from_image(
        self,
        images: list[UploadFile] = File(...),
        translate_language: str | None = Query(None, alias="translateLanguage"),
    ):
        """
        Create a recipe from an image using OpenAI.
        Optionally specify a language for it to translate the recipe to.
        """

        if not (self.settings.OPENAI_ENABLED and self.settings.OPENAI_ENABLE_IMAGE_SERVICES):
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse.respond("OpenAI image services are not enabled"),
            )

        recipe = await self.service.create_from_images(images, translate_language)
        self.publish_event(
            event_type=EventTypes.recipe_created,
            document_data=EventRecipeData(operation=EventOperation.create, recipe_slug=recipe.slug),
            group_id=recipe.group_id,
            household_id=recipe.household_id,
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
        households: list[UUID4 | str] | None = Query(None),
    ):
        cookbook_data: ReadCookBook | None = None
        if search_query.cookbook:
            if isinstance(search_query.cookbook, UUID):
                cb_match_attr = "id"
            else:
                try:
                    UUID(search_query.cookbook)
                    cb_match_attr = "id"
                except ValueError:
                    cb_match_attr = "slug"
            cookbook_data = self.group_cookbooks.get_one(search_query.cookbook, cb_match_attr)

            if cookbook_data is None:
                raise HTTPException(status_code=404, detail="cookbook not found")

        # We use "group_recipes" here so we can return all recipes regardless of household. The query filter can
        # include a household_id to filter by household.
        # We use "by_user" so we can sort favorites and other user-specific data correctly.
        pagination_response = self.group_recipes.by_user(self.user.id).page_all(
            pagination=q,
            cookbook=cookbook_data,
            categories=categories,
            tags=tags,
            tools=tools,
            foods=foods,
            households=households,
            require_all_categories=search_query.require_all_categories,
            require_all_tags=search_query.require_all_tags,
            require_all_tools=search_query.require_all_tools,
            require_all_foods=search_query.require_all_foods,
            search=search_query.search,
        )

        # merge default pagination with the request's query params
        query_params = q.model_dump() | {**request.query_params}
        pagination_response.set_pagination_guides(
            router.url_path_for("get_all"),
            {k: v for k, v in query_params.items() if v is not None},
        )

        json_compatible_response = orjson.dumps(pagination_response.model_dump(by_alias=True))

        # Response is returned directly, to avoid validation and improve performance
        return JSONBytes(content=json_compatible_response)

    @router.get("/suggestions", response_model=RecipeSuggestionResponse)
    def suggest_recipes(
        self,
        q: RecipeSuggestionQuery = Depends(make_dependable(RecipeSuggestionQuery)),
        foods: list[UUID4] | None = Query(None),
        tools: list[UUID4] | None = Query(None),
    ) -> RecipeSuggestionResponse:
        group_recipes_by_user = get_repositories(
            self.session, group_id=self.group_id, household_id=None
        ).recipes.by_user(self.user.id)

        recipes = group_recipes_by_user.find_suggested_recipes(q, foods, tools)
        response = RecipeSuggestionResponse(items=recipes)
        json_compatible_response = orjson.dumps(response.model_dump(by_alias=True))

        # Response is returned directly, to avoid validation and improve performance
        return JSONBytes(content=json_compatible_response)

    @router.get("/{slug}", response_model=Recipe)
    def get_one(self, slug: str = Path(..., description="A recipe's slug or id")):
        """Takes in a recipe's slug or id and returns all data for a recipe"""
        try:
            recipe = self.service.get_one(slug)
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
                group_id=new_recipe.group_id,
                household_id=new_recipe.household_id,
                message=self.t(
                    "notifications.generic-created-with-url",
                    name=new_recipe.name,
                    url=urls.recipe_url(self.group.slug, new_recipe.slug, self.settings.BASE_URL),
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
                group_id=new_recipe.group_id,
                household_id=new_recipe.household_id,
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
                group_id=recipe.group_id,
                household_id=recipe.household_id,
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=recipe.name,
                    url=urls.recipe_url(self.group.slug, recipe.slug, self.settings.BASE_URL),
                ),
            )

        return recipe

    @router.put("")
    def update_many(self, data: list[Recipe]):
        updated_by_group_and_household: defaultdict[UUID4, defaultdict[UUID4, list[Recipe]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for recipe in data:
            r = self.service.update_one(recipe.id, recipe)  # type: ignore
            updated_by_group_and_household[r.group_id][r.household_id].append(r)

        all_updated: list[Recipe] = []
        if updated_by_group_and_household:
            for group_id, household_dict in updated_by_group_and_household.items():
                for household_id, updated_recipes in household_dict.items():
                    all_updated.extend(updated_recipes)
                    self.publish_event(
                        event_type=EventTypes.recipe_updated,
                        document_data=EventRecipeBulkData(
                            operation=EventOperation.update, recipe_slugs=[r.slug for r in updated_recipes]
                        ),
                        group_id=group_id,
                        household_id=household_id,
                    )

        return all_updated

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
                group_id=recipe.group_id,
                household_id=recipe.household_id,
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=recipe.name,
                    url=urls.recipe_url(self.group.slug, recipe.slug, self.settings.BASE_URL),
                ),
            )

        return recipe

    @router.patch("")
    def patch_many(self, data: list[Recipe]):
        updated_by_group_and_household: defaultdict[UUID4, defaultdict[UUID4, list[Recipe]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for recipe in data:
            r = self.service.patch_one(recipe.id, recipe)  # type: ignore
            updated_by_group_and_household[r.group_id][r.household_id].append(r)

        all_updated: list[Recipe] = []
        if updated_by_group_and_household:
            for group_id, household_dict in updated_by_group_and_household.items():
                for household_id, updated_recipes in household_dict.items():
                    all_updated.extend(updated_recipes)
                    self.publish_event(
                        event_type=EventTypes.recipe_updated,
                        document_data=EventRecipeBulkData(
                            operation=EventOperation.update, recipe_slugs=[r.slug for r in updated_recipes]
                        ),
                        group_id=group_id,
                        household_id=household_id,
                    )

        return all_updated

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
                group_id=recipe.group_id,
                household_id=recipe.household_id,
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=recipe.name,
                    url=urls.recipe_url(self.group.slug, recipe.slug, self.settings.BASE_URL),
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
                group_id=recipe.group_id,
                household_id=recipe.household_id,
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

        new_version = self.recipes.update_image(slug, extension)
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
