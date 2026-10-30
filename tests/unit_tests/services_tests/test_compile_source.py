import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

import mealie.services.openai.transcription as transcription_module
import mealie.services.recipe.import_workflow.steps.compile_source as compile_source_module
from mealie.pkgs.safehttp.fetch import FetchResult
from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.services.recipe.import_workflow.context import WorkflowContext, WorkflowInput, WorkflowOptions
from mealie.services.recipe.import_workflow.steps.compile_source import CompileSourceStep

FACEBOOK_SHARE_URL = "https://www.facebook.com/share/r/1DWziuVHRi/"
FACEBOOK_REEL_URL = "https://www.facebook.com/reel/1433866715330175/"


def html_fetch_result(html: str, url: str) -> FetchResult:
    return FetchResult(html.encode(), 200, url, httpx.Headers(), "utf-8")


def _ctx(url: str) -> WorkflowContext:
    ai = MagicMock()
    ai.provider_settings.audio_provider_enabled = True
    translator = MagicMock()
    translator.t.side_effect = lambda key: key
    return WorkflowContext(
        input=WorkflowInput(url=url),
        options=WorkflowOptions(),
        repos=MagicMock(),
        translator=translator,
        ai=ai,
        on_progress=AsyncMock(),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("caption", ["", "Watch my cooking reel!"])
async def test_share_url_is_compiled_as_video_after_redirect(monkeypatch: pytest.MonkeyPatch, caption: str):
    downloaded: list[str] = []

    async def mock_resilient_fetch(url: str):
        html = "<html>facebook</html>"
        if caption:
            data = {"video": {"id": "1433866715330175", "creation_story": {"message": {"text": caption}}}}
            html += (
                f'<meta property="og:url" content="{FACEBOOK_REEL_URL}">'
                f'<script type="application/json">{json.dumps(data)}</script>'
                '<script type="application/ld+json">{"@type":"VideoObject"}</script>'
            )
        return html_fetch_result(html, FACEBOOK_REEL_URL)

    def mock_download_video(url: str, temp_path: Path):
        downloaded.append(url)
        return {
            "audio": temp_path / "mealie.mp3",
            "subtitle": None,
            "title": "A reel",
            "description": "desc",
            "thumbnail_url": None,
            "transcription": "mix flour and water",
        }

    async def mock_resolve_transcription(video_data, openai_service, before_transcribe=None):
        return video_data["transcription"]

    monkeypatch.setattr(compile_source_module, "resilient_fetch", mock_resilient_fetch)
    monkeypatch.setattr(transcription_module, "download_video", mock_download_video)
    monkeypatch.setattr(transcription_module, "resolve_transcription", mock_resolve_transcription)

    ctx = _ctx(FACEBOOK_SHARE_URL)
    ctx.ai.get_response = AsyncMock(return_value=OpenAICompiledSource(contains_recipe=False, content=""))
    await CompileSourceStep().run(ctx)

    assert downloaded == [FACEBOOK_REEL_URL]
    assert ctx.compiled_source is not None
    assert "mix flour and water" in ctx.compiled_source.content
    assert ctx.input.url == FACEBOOK_SHARE_URL


@pytest.mark.asyncio
@pytest.mark.parametrize("audio_enabled", [False, True])
@pytest.mark.parametrize("url", [FACEBOOK_SHARE_URL, FACEBOOK_REEL_URL])
@pytest.mark.parametrize("video_metadata", [False, True])
async def test_facebook_caption_is_read_before_audio(
    monkeypatch: pytest.MonkeyPatch, audio_enabled: bool, url: str, video_metadata: bool
):
    caption = "Chicken Alfredo: 1 cup milk, 2 tbsp flour. Whisk and simmer for 5 minutes."
    data = {"data": {"video": {"id": "1433866715330175", "creation_story": {"message": {"text": caption}}}}}
    html = (
        f'<meta property="og:url" content="{FACEBOOK_REEL_URL}">'
        f'<script type="application/json">{json.dumps(data)}</script><body>Facebook</body>'
    )
    if video_metadata:
        html += '<script type="application/ld+json">{"@type":"VideoObject","name":"A cooking reel"}</script>'
    monkeypatch.setattr(
        compile_source_module, "resilient_fetch", AsyncMock(return_value=html_fetch_result(html, FACEBOOK_REEL_URL))
    )
    download = MagicMock(side_effect=AssertionError("A caption recipe must not download audio"))
    monkeypatch.setattr(transcription_module, "download_video", download)
    ctx = _ctx(url)
    ctx.ai.provider_settings.audio_provider_enabled = audio_enabled
    ctx.ai.get_response = AsyncMock(return_value=OpenAICompiledSource(contains_recipe=True, content=caption))

    await CompileSourceStep().run(ctx)

    download.assert_not_called()
    assert caption in ctx.ai.get_response.call_args.args[1]
    assert ctx.compiled_source is not None
    assert ctx.compiled_source.content == caption
    assert ctx.input.url == url
