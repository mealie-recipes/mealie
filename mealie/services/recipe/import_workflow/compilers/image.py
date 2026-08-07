import os

from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.services.openai import OpenAILocalImage
from mealie.services.openai.content import truncate_source_content

from .base import COMPILE_SOURCE_PROMPT, SourceCompiler


class ImageCompiler(SourceCompiler):
    """Reads uploaded images. Runs on the group's image provider, since it needs vision."""

    progress_key = "recipe.create-progress.reading-images-with-ai"
    requires_content = False

    def can_compile(self) -> bool:
        return bool(self.ctx.input.images)

    async def compile(self) -> OpenAICompiledSource | None:
        images = self.ctx.input.images
        attachments = [OpenAILocalImage(filename=os.path.basename(image), path=image) for image in images]

        message_parts = [
            f"Attached {'are' if len(images) > 1 else 'is'} {len(images)} "
            f"{'images' if len(images) > 1 else 'image'} of a single recipe."
        ]
        if self.content:
            message_parts.append(f"The following text accompanies the {'images' if len(images) > 1 else 'image'}:")
            message_parts.append(truncate_source_content(self.content))

        return await self.ctx.ai.get_response(
            self.ctx.ai.get_prompt(COMPILE_SOURCE_PROMPT),
            "\n".join(message_parts),
            response_schema=OpenAICompiledSource,
            attachments=attachments,
        )
