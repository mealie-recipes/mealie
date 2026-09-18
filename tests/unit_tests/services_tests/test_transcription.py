from unittest.mock import Mock

import pytest

from mealie.services.openai import transcription
from mealie.services.recipe.import_workflow.compilers.transcription import TranscriptionCompiler


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
        ("https://www.facebook.com/reel/1433866715330175/", True),
        ("https://www.facebook.com/share/r/1DWziuVHRi/", False),
        ("https://example.com/recipe", False),
        ("", False),
    ],
)
def test_is_video_url(url: str, expected: bool):
    """
    yt-dlp's Facebook extractor matches /reel/ but not /share/r/ share links.
    Those are handled by following redirects in the import workflow.
    """

    assert transcription.is_video_url(url) is expected


def test_transcription_compiler_uses_resolved_url(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        transcription,
        "is_video_url",
        lambda url: url == "https://www.facebook.com/reel/1433866715330175/",
    )

    ctx = Mock()
    ctx.input.url = "https://www.facebook.com/share/r/1DWziuVHRi/"
    ctx.resolved_url = "https://www.facebook.com/reel/1433866715330175/"
    ctx.ai.provider_settings.audio_provider_enabled = True

    compiler = TranscriptionCompiler(ctx)
    assert compiler.can_compile() is True
    assert compiler._url() == ctx.resolved_url
