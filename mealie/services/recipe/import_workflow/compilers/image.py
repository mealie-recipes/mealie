import os

from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.services.openai import OpenAILocalImage

from .base import COMPILE_SOURCE_PROMPT, SourceCompiler, SourceType


class ImageCompiler(SourceCompiler):
    """Reads uploaded images. Runs on the group's image provider, since it needs vision."""

    source_type = SourceType.IMAGES
    progress_key = "recipe.create-progress.reading-images-with-ai"

    def can_compile(self) -> bool:
        return bool(self.ctx.input.images)

    async def compile(self) -> OpenAICompiledSource | None:
        images = self.ctx.input.images
        attachments = [OpenAILocalImage(filename=os.path.basename(image), path=image) for image in images]

        noun = "images" if len(images) > 1 else "image"
        message = f"Attached {'are' if len(images) > 1 else 'is'} {len(images)} {noun} of a single recipe."

        return await self.ctx.ai.get_response(
            self.ctx.ai.get_prompt(COMPILE_SOURCE_PROMPT),
            message,
            response_schema=OpenAICompiledSource,
            attachments=attachments,
        )
