import shutil
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import UploadFile

from mealie.core.dependencies.dependencies import get_temporary_path
from mealie.pkgs.img.pdf import is_pdf, render_pdf
from mealie.schema.recipe.recipe import RecipeDraft, RecipeOut
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
    ) -> RecipeOut:
        """
        Creates a recipe from any combination of content, images, and a URL.

        Each PDF becomes one image per page, and its text is added to the content.
        The first image that is not a PDF, if any, becomes the recipe's cover image.
        """

        with get_temporary_path() as temp_path:
            local_files = self._store_images(images or [], temp_path)
            cover_image = next((path for path in local_files if not is_pdf(path)), None)
            local_images, pdf_text = self._expand_pdfs(local_files)
            if pdf_text:
                content = f"{content}\n\n{pdf_text}" if content else pdf_text

            recipe_data = await self.build_recipe(
                content=content,
                images=local_images,
                url=url,
                translate_language=translate_language,
                create_new_organizers=create_new_organizers,
                on_progress=on_progress,
            )

            recipe = self.create_one(recipe_data)
            if cover_image:
                with open(cover_image, "rb") as f:
                    RecipeDataService(recipe.id).write_image(f.read(), "webp")
                # write_image only writes the files; record the cover on the recipe as the image upload route does
                recipe.image = self.group_recipes.update_image(recipe.slug, "webp")

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
    ) -> RecipeDraft:
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

    @staticmethod
    def _expand_pdfs(files: list[Path]) -> tuple[list[Path], str]:
        """Replaces each PDF with images of its pages. Returns the images and the text of all PDFs."""
        images: list[Path] = []
        texts: list[str] = []
        for path in files:
            if not is_pdf(path):
                images.append(path)
                continue

            pages, text = render_pdf(path)
            images.extend(pages)
            if text:
                texts.append(f"Text from {path.name}:\n\n{text}")

        return images, "\n\n".join(texts)

    def _validate_providers(self, ai_service: OpenAIService, *, has_images: bool) -> None:
        settings = ai_service.provider_settings
        if not (settings and settings.ai_enabled):
            raise AIProviderNotEnabledError(self.t("recipe.import-errors.ai-not-enabled"))

        if has_images and not settings.image_provider_enabled:
            raise AIProviderNotEnabledError(self.t("recipe.import-errors.image-provider-not-enabled"))
