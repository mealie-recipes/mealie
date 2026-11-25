import asyncio
import shutil
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import UploadFile

from mealie.core.dependencies.dependencies import get_temporary_path
from mealie.schema.recipe.recipe import RecipeDraft, RecipeOut
from mealie.services.openai import OpenAIService
from mealie.services.scraper.scraper import finalize_scraped_recipe

from .document_text_extraction import (
    DocumentExtractionError,
    EmptyPdfTextError,
    extract_images_from_pdf,
    extract_text_from_document,
)
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


class DocumentReadError(Exception):
    """Raised when an uploaded document can't be read; the message names the offending file."""

    pass


class AIRecipeService(RecipeService):
    """Creates recipes from arbitrary source material by running the recipe import workflow."""

    async def create_from_ai(
        self,
        *,
        content: str | None = None,
        images: list[UploadFile] | None = None,
        url: str | None = None,
        documents: list[UploadFile] | None = None,
        translate_language: str | None = None,
        create_new_organizers: bool = False,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> RecipeOut:
        """
        Creates a recipe from any combination of content, images, a URL, and uploaded documents.

        Text is extracted from each document, and images embedded in a scanned PDF are routed
        through the same vision pipeline as uploaded images. Raises DocumentReadError if a
        document can't be read.

        The first image, if any, becomes the recipe's cover image.
        """

        document_content, document_images = await self._extract_document_content(documents or [])

        with get_temporary_path() as temp_path:
            local_images = self._store_images(images or [], temp_path)
            local_images += self._store_document_images(document_images, temp_path)

            recipe_data = await self.build_recipe(
                content=content,
                images=local_images,
                url=url,
                document_content=document_content,
                translate_language=translate_language,
                create_new_organizers=create_new_organizers,
                on_progress=on_progress,
            )

            recipe = self.create_one(recipe_data)
            if local_images:
                with open(local_images[0], "rb") as f:
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
        document_content: str | None = None,
        translate_language: str | None = None,
        create_new_organizers: bool = False,
        on_progress: Callable[[str], Awaitable[None]] | None = None,
    ) -> RecipeDraft:
        """
        Compiles the given source material into a recipe.

        The recipe is not persisted; that's up to the caller.
        """

        workflow_input = WorkflowInput(content=content, images=images or [], url=url, document_content=document_content)
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
    async def _extract_one_document(document: UploadFile) -> tuple[str | None, list[tuple[str, bytes]]]:
        """
        Reads one uploaded document and extracts either its text, or, for a scanned PDF with no
        text layer, its embedded page images. Parsing runs in a thread so it can't block the event loop.
        """
        file_bytes = await document.read()
        filename = document.filename or ""

        try:
            return await asyncio.to_thread(extract_text_from_document, file_bytes, filename), []
        except EmptyPdfTextError:
            pass
        except DocumentExtractionError as e:
            raise DocumentReadError(f"Couldn't read {filename}: {e}") from e

        try:
            document_images = await asyncio.to_thread(extract_images_from_pdf, file_bytes)
        except DocumentExtractionError as e:
            raise DocumentReadError(f"Couldn't read {filename}: {e}") from e

        if not document_images:
            raise DocumentReadError(f"Couldn't read {filename}: doesn't contain readable text or images.")

        return None, document_images

    async def _extract_document_content(
        self, documents: list[UploadFile]
    ) -> tuple[str | None, list[tuple[str, bytes]]]:
        """
        Reads every uploaded document and extracts their text and/or (for a scanned PDF with no
        text layer) embedded page images. Returns (None, []) if no documents were given.

        A single document's extracted text is returned as-is; with more than one, each is
        labelled with its filename so the merged text still shows which file each part came from.
        """
        texts: list[tuple[str, str]] = []
        document_images: list[tuple[str, bytes]] = []
        for document in documents:
            text, images = await self._extract_one_document(document)
            if text is not None:
                texts.append((document.filename or "", text))
            document_images.extend(images)

        if not texts:
            document_content = None
        elif len(texts) == 1:
            document_content = texts[0][1]
        else:
            document_content = "\n\n".join(f"## {filename}\n\n{text}" for filename, text in texts)

        return document_content, document_images

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
    def _store_document_images(document_images: list[tuple[str, bytes]], temp_path: Path) -> list[Path]:
        """Writes images extracted from an uploaded document (e.g. a scanned PDF's pages) to disk."""
        local_images: list[Path] = []
        for index, (filename, image_bytes) in enumerate(document_images):
            # pypdf's embedded image names are only unique within a page, so index-prefix them
            # to avoid collisions between pages when writing into the same temp directory
            image_path = temp_path.joinpath(f"{index}-{Path(filename).name}")
            image_path.write_bytes(image_bytes)
            local_images.append(image_path)

        return local_images

    def _validate_providers(self, ai_service: OpenAIService, *, has_images: bool) -> None:
        settings = ai_service.provider_settings
        if not (settings and settings.ai_enabled):
            raise AIProviderNotEnabledError(self.t("recipe.import-errors.ai-not-enabled"))

        if has_images and not settings.image_provider_enabled:
            raise AIProviderNotEnabledError(self.t("recipe.import-errors.image-provider-not-enabled"))
