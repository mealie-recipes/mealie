import asyncio
from collections import defaultdict
from collections.abc import AsyncIterable, Awaitable, Callable
from shutil import copyfileobj
from typing import Annotated
from uuid import UUID

import orjson
import sqlalchemy
import sqlalchemy.exc
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
from fastapi.sse import EventSourceResponse, ServerSentEvent
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
from mealie.schema.recipe.recipe_scraper import ScrapeRecipeAI, ScrapeRecipeTest
from mealie.schema.recipe.recipe_suggestion import RecipeSuggestionQuery, RecipeSuggestionResponse
from mealie.schema.recipe.request_helpers import (
    RecipeDuplicate,
    UpdateImageResponse,
)
from mealie.schema.response import PaginationBase, PaginationQuery
from mealie.schema.response.pagination import RecipeSearchQuery
from mealie.schema.response.responses import (
    ErrorResponse,
    SSEDataEventDone,
    SSEDataEventMessage,
    SSEDataEventStatus,
    SuccessResponse,
)
from mealie.services import urls
from mealie.services.event_bus_service.event_types import (
    EventOperation,
    EventRecipeBulkData,
    EventRecipeBulkReportData,
    EventRecipeData,
    EventTypes,
)
from mealie.services.openai import OpenAINotEnabledException
from mealie.services.recipe.ai_recipe_service import AIProviderNotEnabledError, AIRecipeService
from mealie.services.recipe.import_workflow.exceptions import NoRecipeDataError
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

ASSET_ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "gif", "webp", "bmp", "avif", "txt", "md", "csv", "json"}

router = UserAPIRouter(prefix="/recipes", route_class=MealieCrudRoute)


@controller(router)
class RecipeController(BaseRecipeController):
    def handle_exceptions(self, ex: Exception) -> None:
        thrownType = type(ex)

        if thrownType == exceptions.PermissionDenied:
            self.logger.error("Permission Denied on recipe controller action")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=ErrorResponse.respond(message="Permission Denied")
            )
        elif thrownType == exceptions.NoEntryFound:
            self.logger.error("No Entry Found on recipe controller action")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ErrorResponse.respond(message="No Entry Found")
            )
        elif thrownType == sqlalchemy.exc.IntegrityError:
            self.logger.error("SQL Integrity Error on recipe controller action")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorResponse.respond(message="Recipe already exists")
            )
        elif thrownType == exceptions.RecursiveRecipe:
            self.logger.error("Recursive Recipe Link Error on recipe controller action")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse.respond(message=self.t("exceptions.recursive-recipe-link")),
            )
        elif thrownType == exceptions.SlugError:
            self.logger.error("Failed to generate a valid slug from recipe name")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse.respond(message="Unable to generate recipe slug"),
            )
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
        try:
            if data.use_openai:
                # the AI scraper builds a recipe directly, so there's no scraped schema to show
                scraper = RecipeScraperOpenAI(data.url, self.translator, self.repos)
                try:
                    result = await scraper.parse()
                except NoRecipeDataError:
                    result = None

                if result and result[0]:
                    return result[0].model_dump(by_alias=True)

                return "AI was unable to extract a recipe from this URL"

            # Debugger should produce the same result as the scraper sees before cleaning
            if scraped_data := await RecipeScraperPackage(data.url, self.translator, self.repos).scrape_url():
                return scraped_data.schema.data
        except ForceTimeoutException as e:
            raise HTTPException(
                status_code=408, detail=ErrorResponse.respond(message="Recipe Scraping Timed Out")
            ) from e

        return "recipe_scrapers was unable to scrape this URL"

    @router.post("/create/html-or-json", status_code=201, response_model=str)
    async def create_recipe_from_html_or_json(self, req: ScrapeRecipeData) -> str:
        """Takes in raw HTML or a https://schema.org/Recipe object as a JSON string and parses it like a URL"""

        if req.data.startswith("{"):
            req.data = RecipeScraperPackage.ld_json_to_html(req.data)

        async for event in self._create_recipe_from_web(req):
            if isinstance(event.data, SSEDataEventDone):
                return event.data.slug
            if isinstance(event.data, SSEDataEventMessage) and event.event == SSEDataEventStatus.ERROR:
                raise HTTPException(status_code=400, detail=ErrorResponse.respond(message=event.data.message))

        # This should never be reachable, since we should always hit DONE or hit an exception/ERROR
        raise HTTPException(status_code=500, detail=ErrorResponse.respond(message="Unknown Error"))

    @router.post("/create/html-or-json/stream", response_class=EventSourceResponse)
    async def create_recipe_from_html_or_json_stream(self, req: ScrapeRecipeData) -> AsyncIterable[ServerSentEvent]:
        """
        Takes in raw HTML or a https://schema.org/Recipe object as a JSON string and parses it like a URL,
        streaming progress via SSE
        """

        if req.data.startswith("{"):
            req.data = RecipeScraperPackage.ld_json_to_html(req.data)

        async for event in self._create_recipe_from_web(req):
            yield event

    @router.post("/create/url", status_code=201, response_model=str)
    async def parse_recipe_url(self, req: ScrapeRecipe) -> str:
        """Takes in a URL and attempts to scrape data and load it into the database"""

        async for event in self._create_recipe_from_web(req):
            if isinstance(event.data, SSEDataEventDone):
                return event.data.slug
            if isinstance(event.data, SSEDataEventMessage) and event.event == SSEDataEventStatus.ERROR:
                raise HTTPException(status_code=400, detail=ErrorResponse.respond(message=event.data.message))

        # This should never be reachable, since we should always hit DONE or hit an exception/ERROR
        raise HTTPException(status_code=500, detail=ErrorResponse.respond(message="Unknown Error"))

    @router.post("/create/url/stream", response_class=EventSourceResponse)
    async def parse_recipe_url_stream(self, req: ScrapeRecipe) -> AsyncIterable[ServerSentEvent]:
        """
        Takes in a URL and attempts to scrape data and load it into the database,
        streaming progress via SSE
        """

        async for event in self._create_recipe_from_web(req):
            yield event

    def _error_message(self, ex: Exception) -> str:
        """
        Turn an exception raised during recipe creation into something worth showing a user.

        The AI import page renders this message as-is, so every failure has to map to a
        translated string. An exception's own text is not usable here: it carries provider and
        library internals, and a bare class name like "OpenAIServiceError" is no better. Anything
        unrecognized falls back to a generic message, and the caller logs the exception itself.
        """

        if isinstance(ex, exceptions.RateLimitError):
            return self.t("exceptions.rate-limit-error")

        if isinstance(ex, NoRecipeDataError | AIProviderNotEnabledError):
            # these are raised with an already-translated message
            if message := str(ex):
                return message

        if isinstance(ex, OpenAINotEnabledException):
            return self.t("recipe.import-errors.ai-not-enabled")

        if isinstance(ex, exceptions.VideoDownloadError):
            return self.t("recipe.import-errors.video-download-failed")

        if isinstance(ex, exceptions.OpenAIServiceError):
            return self.t("recipe.import-errors.ai-request-failed")

        if isinstance(ex, HTTPException):
            # scraper failures carry a `ParserErrors` value (e.g. BAD_RECIPE_DATA), which the URL
            # and HTML importers expect verbatim. They render their own message rather than this one
            detail = ex.detail
            if isinstance(detail, dict) and (details := detail.get("details")):
                return str(details)
            if isinstance(detail, str) and detail:
                return detail

        return self.t("recipe.import-errors.unknown-error")

    async def _stream_recipe_creation(
        self, create: Callable[[Callable[[str], Awaitable[None]]], Awaitable[str]]
    ) -> AsyncIterable[ServerSentEvent]:
        """
        Run a recipe creation coroutine, returning progress via SSE.

        `create` is passed a progress callback, and returns the new recipe's slug.
        Events will continue to be yielded until:
            - The recipe is created, emitting:
                - event=SSEDataEventStatus.DONE
                - data=SSEDataEventDone(...)
            - An exception is raised, emitting:
                - event=SSEDataEventStatus.ERROR
                - data=SSEDataEventMessage(...)
        """

        queue: asyncio.Queue[ServerSentEvent | None] = asyncio.Queue()

        async def on_progress(message: str) -> None:
            await queue.put(
                ServerSentEvent(
                    data=SSEDataEventMessage(message=message),
                    event=SSEDataEventStatus.PROGRESS,
                )
            )

        async def run() -> None:
            try:
                slug = await create(on_progress)
                await queue.put(
                    ServerSentEvent(
                        data=SSEDataEventDone(slug=slug),
                        event=SSEDataEventStatus.DONE,
                    )
                )
            except Exception as e:
                self.logger.exception("Error in streaming recipe creation")
                await queue.put(
                    ServerSentEvent(
                        data=SSEDataEventMessage(message=self._error_message(e)),
                        event=SSEDataEventStatus.ERROR,
                    )
                )
            finally:
                await queue.put(None)

        asyncio.create_task(run())
        while (event := await queue.get()) is not None:
            yield event

    def _create_recipe_from_web(self, req: ScrapeRecipe | ScrapeRecipeData) -> AsyncIterable[ServerSentEvent]:
        """Create a recipe from the web, returning progress via SSE"""

        if isinstance(req, ScrapeRecipeData):
            html = req.data
            url = req.url or ""
        else:
            html = None
            url = req.url

        async def create(on_progress: Callable[[str], Awaitable[None]]) -> str:
            recipe, extras = await create_from_html(
                url,
                self.repos,
                self.translator,
                html,
                on_progress=on_progress,
                include_tags=req.include_tags,
                include_categories=req.include_categories,
            )
            return self._finish_recipe_from_web(req, recipe, extras)

        return self._stream_recipe_creation(create)

    def _finish_recipe_from_web(self, req: ScrapeRecipe | ScrapeRecipeData, recipe: Recipe, extras: object) -> str:
        if req.include_tags:
            ctx = ScraperContext(self.repos)
            recipe.tags = extras.use_tags(ctx)  # type: ignore

        if req.include_categories:
            ctx = ScraperContext(self.repos)
            recipe.recipe_category = extras.use_categories(ctx)  # type: ignore

        new_recipe = self.service.create_one(recipe)
        self._publish_recipe_created(new_recipe)
        return new_recipe.slug

    def _publish_recipe_created(self, new_recipe: Recipe) -> None:
        if not new_recipe:
            return

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

    # =======================================================================
    # AI Operations

    @router.post("/create/ai", status_code=201, response_model=str)
    async def create_recipe_with_ai(
        self,
        content: Annotated[str | None, Form()] = None,
        url: Annotated[str | None, Form()] = None,
        translate_language: Annotated[str | None, Form(alias="translateLanguage")] = None,
        create_new_organizers: Annotated[bool, Form(alias="createNewOrganizers")] = False,
        images: list[UploadFile] = File(default_factory=list),
    ) -> str:
        """
        Create a recipe from any combination of content (HTML, JSON, or text), images, and a URL,
        using AI. Optionally specify a language for it to translate the recipe to.
        """

        req = ScrapeRecipeAI(
            content=content,
            url=url,
            translate_language=translate_language,
            create_new_organizers=create_new_organizers,
        )
        async for event in self._create_recipe_with_ai(req, images):
            if isinstance(event.data, SSEDataEventDone):
                return event.data.slug
            if isinstance(event.data, SSEDataEventMessage) and event.event == SSEDataEventStatus.ERROR:
                raise HTTPException(status_code=400, detail=ErrorResponse.respond(message=event.data.message))

        # This should never be reachable, since we should always hit DONE or hit an exception/ERROR
        raise HTTPException(status_code=500, detail=ErrorResponse.respond(message="Unknown Error"))

    @router.post("/create/ai/stream", response_class=EventSourceResponse)
    async def create_recipe_with_ai_stream(
        self,
        content: Annotated[str | None, Form()] = None,
        url: Annotated[str | None, Form()] = None,
        translate_language: Annotated[str | None, Form(alias="translateLanguage")] = None,
        create_new_organizers: Annotated[bool, Form(alias="createNewOrganizers")] = False,
        images: list[UploadFile] = File(default_factory=list),
    ) -> AsyncIterable[ServerSentEvent]:
        """
        Create a recipe from any combination of content (HTML, JSON, or text), images, and a URL,
        using AI, streaming progress via SSE
        """

        req = ScrapeRecipeAI(
            content=content,
            url=url,
            translate_language=translate_language,
            create_new_organizers=create_new_organizers,
        )
        async for event in self._create_recipe_with_ai(req, images):
            yield event

    def _create_recipe_with_ai(self, req: ScrapeRecipeAI, images: list[UploadFile]) -> AsyncIterable[ServerSentEvent]:
        """Create a recipe using AI, returning progress via SSE"""

        ai_service = AIRecipeService(self.repos, self.user, self.household, translator=self.translator)

        async def create(on_progress: Callable[[str], Awaitable[None]]) -> str:
            recipe = await ai_service.create_from_ai(
                content=req.content,
                images=images,
                url=req.url,
                translate_language=req.translate_language,
                create_new_organizers=req.create_new_organizers,
                on_progress=on_progress,
            )
            self._publish_recipe_created(recipe)
            return recipe.slug

        return self._stream_recipe_creation(create)

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

    @router.post("/create/image", status_code=201, deprecated=True, include_in_schema=False)
    async def create_recipe_from_image(
        self,
        images: list[UploadFile] = File(...),
        translate_language: str | None = Query(None, alias="translateLanguage"),
    ):
        """
        Deprecated in favor of `/create/ai`, which accepts images alongside other content.
        Kept so existing integrations keep working.
        """

        req = ScrapeRecipeAI(translate_language=translate_language)
        async for event in self._create_recipe_with_ai(req, images):
            if isinstance(event.data, SSEDataEventDone):
                return event.data.slug
            if isinstance(event.data, SSEDataEventMessage) and event.event == SSEDataEventStatus.ERROR:
                raise HTTPException(status_code=400, detail=ErrorResponse.respond(message=event.data.message))

        # This should never be reachable, since we should always hit DONE or hit an exception/ERROR
        raise HTTPException(status_code=500, detail=ErrorResponse.respond(message="Unknown Error"))

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

    @router.post("/{slug}/image", response_model=UpdateImageResponse, tags=["Recipe: Images and Assets"])
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
        return UpdateImageResponse(image=recipe.image)

    @router.put("/{slug}/image", response_model=UpdateImageResponse, tags=["Recipe: Images and Assets"])
    def update_recipe_image(self, slug: str, image: bytes = File(...), extension: str = Form(...)):
        try:
            new_version = self.service.update_recipe_image(slug, image, extension)
            return UpdateImageResponse(image=new_version)
        except Exception as e:
            self.handle_exceptions(e)
            return None

    @router.delete("/{slug}/image", tags=["Recipe: Images and Assets"])
    def delete_recipe_image(self, slug: str):
        try:
            self.service.delete_recipe_image(slug)
            return SuccessResponse.respond(message=self.t("recipe.recipe-image-deleted"))
        except Exception as e:
            self.handle_exceptions(e)
            return None

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

        extension = extension.lower()
        if extension not in ASSET_ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Unsupported file extension")

        file_slug = slugify(name)
        if not extension or not file_slug:
            raise HTTPException(status_code=400, detail="Missing required fields")

        file_name = f"{file_slug}.{extension}"
        asset_in = RecipeAsset(name=name, icon=icon, file_name=file_name)

        recipe = self.service.get_one(slug)

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

        if recipe.assets is not None:
            recipe.assets.append(asset_in)

        self.service.update_one(slug, recipe)

        return asset_in
