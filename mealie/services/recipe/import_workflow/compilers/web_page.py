from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.services.openai.content import extract_page_content

from .base import COMPILE_SOURCE_PROMPT, SourceCompiler


class WebPageCompiler(SourceCompiler):
    """
    Reads webpage content that has no usable structured data, so the recipe has to be picked
    out of the surrounding page text.
    """

    progress_key = "recipe.create-progress.reading-source-with-ai"

    def can_compile(self) -> bool:
        return bool(self.content)

    async def compile(self) -> OpenAICompiledSource | None:
        content = self.content or ""
        image_url: str | None = None

        try:
            content, image_url = extract_page_content(content)
        except ValueError:
            return None

        message_parts = ["The following content was extracted from a webpage."]
        if image_url:
            message_parts.append(f"The page's primary image is: {image_url}")
        message_parts.append(content)

        compiled = await self.ctx.ai.get_response(
            self.ctx.ai.get_prompt(COMPILE_SOURCE_PROMPT),
            "\n".join(message_parts),
            response_schema=OpenAICompiledSource,
        )

        if compiled and not compiled.image_url:
            compiled.image_url = image_url

        return compiled
