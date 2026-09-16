import pytest

import mealie.services.openai.transcription as transcription_module


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
