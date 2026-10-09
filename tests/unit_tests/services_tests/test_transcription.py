from unittest.mock import Mock

import pytest

import mealie.services.openai.transcription as transcription_module
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


class _SettingsStub:
    YTDLP_COOKIEFILE: str | None = None


@pytest.fixture()
def settings_stub(monkeypatch):
    s = _SettingsStub()

    def _fake_get_app_settings():
        return s

    monkeypatch.setattr(transcription_module, "get_app_settings", _fake_get_app_settings)
    return s


class _FakeYoutubeDL:
    """Records the ydl_opts it was constructed with instead of hitting the network."""

    last_opts: dict | None = None

    def __init__(self, opts: dict):
        _FakeYoutubeDL.last_opts = opts

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def extract_info(self, url: str, download: bool = True):
        return {"title": "Fake Title", "description": "Fake Description", "thumbnail": None}


@pytest.fixture()
def fake_yt_dlp(monkeypatch):
    _FakeYoutubeDL.last_opts = None
    monkeypatch.setattr("yt_dlp.YoutubeDL", _FakeYoutubeDL)
    return _FakeYoutubeDL


def test_download_video_omits_cookiefile_by_default(settings_stub, fake_yt_dlp, tmp_path):
    transcription_module.download_video("https://example.com/video", tmp_path)

    assert "cookiefile" not in fake_yt_dlp.last_opts


def test_download_video_passes_configured_cookiefile(settings_stub, fake_yt_dlp, tmp_path):
    settings_stub.YTDLP_COOKIEFILE = "/data/cookies.txt"

    transcription_module.download_video("https://example.com/video", tmp_path)

    assert fake_yt_dlp.last_opts["cookiefile"] == "/data/cookies.txt"
