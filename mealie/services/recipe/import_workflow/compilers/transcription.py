import asyncio

from mealie.core.dependencies.dependencies import get_temporary_path
from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.services.openai import transcription

from .base import SourceCompiler, SourceType


class TranscriptionCompiler(SourceCompiler):
    """
    Compiles a video into its transcript. The audio provider does the transcribing, but the
    transcript itself is already a faithful record of the source, so no further AI call is made.
    """

    source_type = SourceType.URL
    progress_key = "recipe.create-progress.downloading-video"

    def can_compile(self) -> bool:
        url = self.ctx.input.url
        if not url:
            return False

        settings = self.ctx.ai.provider_settings
        if not (settings and settings.audio_provider_enabled):
            return False

        return transcription.is_video_url(url)

    async def compile(self) -> OpenAICompiledSource | None:
        url = self.ctx.input.url or ""

        with get_temporary_path() as temp_path:
            video_data = await asyncio.to_thread(transcription.download_video, url, temp_path)

            async def report_transcribing() -> None:
                await self.ctx.report_progress("recipe.create-progress.transcribing-audio-with-ai")

            transcript = await transcription.resolve_transcription(
                video_data, self.ctx.ai, before_transcribe=report_transcribing
            )

        if not transcript:
            self.logger.error("Could not extract a transcript (no data)")
            return None

        content_parts = [f"# {video_data['title']}"] if video_data["title"] else []
        if video_data["description"]:
            content_parts.append(f"## Video description\n\n{video_data['description']}")
        content_parts.append(f"## Video transcript\n\n{transcript}")

        return OpenAICompiledSource(
            contains_recipe=True,
            content="\n\n".join(content_parts),
            language=None,
            image_url=video_data["thumbnail_url"],
        )
