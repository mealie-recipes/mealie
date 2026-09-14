import shutil
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import UploadFile

from mealie.core.dependencies.dependencies import get_temporary_path
from mealie.schema.recipe.recipe import Recipe
from mealie.services.openai import OpenAIService
from mealie.services.scraper.scraper import finalize_scraped_recipe

from .import_workflow import (
    RecipeImportWorkflow,
    WorkflowContext,
    WorkflowInput,
    WorkflowOptions,
)
from .import_workflow.exceptions import NoRecipeDataError
from .recipe_data_service import RecipeDataService
from .recipe_service import RecipeService


class AIProviderNotEnabledError(Exception):
    """Raised when the group hasn't configured the AI provider a request needs."""

    pass


class AIRecipeService(RecipeService):
    """Creates recipes from arbitrary source material by running the recipe import workflow."""

    async def create_from_ai(
        self,
        *,
        content: str | None = None,
        images: list[UploadFile] | None = None,
        url: str | None = None,
        translate_language: str | None = None,
        create_new_organizers: bool = False,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> Recipe:
        """
        Creates a recipe from any combination of content, images, and a URL.

        The first image, if any, becomes the recipe's cover image.
        """

        with get_temporary_path() as temp_path:
            local_images = self._store_images(images or [], temp_path)

            recipe_data = await self.build_recipe(
                content=content,
                images=local_images,
                url=url,
                translate_language=translate_language,
                create_new_organizers=create_new_organizers,
                on_progress=on_progress,
            )

            recipe = self.create_one(recipe_data)
            if local_images:
                with open(local_images[0], "rb") as f:
                    RecipeDataService(recipe.id).write_image(f.read(), "webp")

            return recipe

    async def build_recipe(
        self,
        *,
        content: str | None = None,
        images: list[Path] | None = None,
        url: str | None = None,
        translate_language: str | None = None,
        create_new_organizers: bool = False,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> Recipe:
        """
        Compiles the given source material into a recipe.

        The recipe is not persisted; that's up to the caller.
        """

        workflow_input = WorkflowInput(content=content, images=images or [], url=url)
        if workflow_input.is_empty:
            raise NoRecipeDataError(self.t("recipe.import-errors.no-source"))

        ai_service = OpenAIService(self.repos)
        self._validate_providers(ai_service, has_images=bool(workflow_input.images))

        ctx = WorkflowContext(
            input=workflow_input,
            options=WorkflowOptions(
                translate_language=translate_language,
                create_new_organizers=create_new_organizers,
            ),
            repos=self.repos,
            user=self.user,
            household=self.household,
            translator=self.translator,
            ai=ai_service,
            on_progress=on_progress,
        )

        result = await RecipeImportWorkflow().run(ctx)
        return await finalize_scraped_recipe(result.recipe, self.translator, on_progress=on_progress)

    @staticmethod
    def _store_images(images: list[UploadFile], temp_path: Path) -> list[Path]:
        local_images: list[Path] = []
        for image in images:
            if not image.filename:
                continue

            image_path = temp_path.joinpath(Path(image.filename).name)
            with image_path.open("wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            local_images.append(image_path)

        return local_images

    def _validate_providers(self, ai_service: OpenAIService, *, has_images: bool) -> None:
        settings = ai_service.provider_settings
        if not (settings and settings.ai_enabled):
            raise AIProviderNotEnabledError(self.t("recipe.import-errors.ai-not-enabled"))

        if has_images and not settings.image_provider_enabled:
            raise AIProviderNotEnabledError(self.t("recipe.import-errors.image-provider-not-enabled"))
