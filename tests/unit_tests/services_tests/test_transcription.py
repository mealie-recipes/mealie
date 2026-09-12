from unittest.mock import Mock

import pytest

import mealie.services.openai.transcription as transcription_module
from mealie.services.recipe.import_workflow.compilers.transcription import TranscriptionCompiler


@pytest.mark.parametrize(
    "url",
    [
        "https://facebook.com/share/r/1DWziuVHRi/",
        "https://www.facebook.com/share/r/1DWziuVHRi/",
        "https://m.facebook.com/share/r/1DWziuVHRi/",
        "https://www.facebook.com/share/r/1DWziuVHRi?mibextid=test",
        "http://www.facebook.com/share/r/1DWziuVHRi/",
    ],
)
def test_is_video_url_accepts_facebook_reel_shares(monkeypatch: pytest.MonkeyPatch, url: str):
    monkeypatch.setattr(transcription_module, "get_yt_dlp_extractors", lambda: [])

    assert transcription_module.is_video_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "",
        "https://example.com/share/r/1DWziuVHRi/",
        "https://notfacebook.com/share/r/1DWziuVHRi/",
        "https://www.facebook.com.example.com/share/r/1DWziuVHRi/",
        "https://www.facebook.com@elsewhere.example/share/r/1DWziuVHRi/",
        "https://www.facebook.com/share/p/1DWziuVHRi/",
        "https://www.facebook.com/share/r/",
        "https://www.facebook.com/share/r/1DWziuVHRi/extra",
        "ftp://www.facebook.com/share/r/1DWziuVHRi/",
        "https://[invalid/share/r/1DWziuVHRi/",
    ],
)
def test_is_video_url_rejects_non_reel_shares(monkeypatch: pytest.MonkeyPatch, url: str):
    monkeypatch.setattr(transcription_module, "get_yt_dlp_extractors", lambda: [])

    assert not transcription_module.is_video_url(url)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.facebook.com/share/r/1DWziuVHRi/", True),
        ("https://www.facebook.com/reel/1433866715330175/", True),
        ("https://www.youtube.com/watch?v=BaW_jenozKc", True),
        ("https://example.com/recipe", False),
    ],
)
def test_is_video_url_with_real_extractors(url: str, expected: bool):
    assert transcription_module.is_video_url(url) is expected


@pytest.mark.parametrize("audio_enabled", [True, False])
def test_facebook_reel_share_transcription_eligibility(audio_enabled: bool):
    ctx = Mock()
    ctx.input.url = "https://www.facebook.com/share/r/1DWziuVHRi/"
    ctx.ai.provider_settings.audio_provider_enabled = audio_enabled

    assert TranscriptionCompiler(ctx).can_compile() is audio_enabled


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
