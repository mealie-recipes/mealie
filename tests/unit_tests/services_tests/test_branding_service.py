from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from mealie.core.settings.directories import AppDirectories
from mealie.routes.spa.manifest import app_icons
from mealie.services import _base_service
from mealie.services.branding.branding_service import BRANDING_FILES, BrandingService, get_branding
from tests.utils import api_routes


@pytest.fixture()
def branding_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Path]:
    """Point the branding service at an empty data folder"""
    monkeypatch.setattr(_base_service, "get_app_dirs", lambda: AppDirectories(tmp_path))
    get_branding.cache_clear()
    yield tmp_path / "branding"
    get_branding.cache_clear()


def write_logo(branding_dir: Path, size: tuple[int, int] = (300, 150), color: str = "#00FF00") -> Path:
    branding_dir.mkdir(parents=True, exist_ok=True)
    logo = branding_dir / "logo.png"
    Image.new("RGBA", size, color).save(logo)
    return logo


def test_no_logo_means_no_branding(branding_dir: Path):
    assert get_branding() is None
    assert all(icon["src"].startswith("/icons/") for icon in app_icons())


def test_generates_every_icon_from_the_logo(branding_dir: Path):
    write_logo(branding_dir)

    branding = BrandingService().load()
    assert branding is not None

    for filename in BRANDING_FILES:
        path = branding.get_file(filename)
        assert path is not None and path.is_file()

    with Image.open(branding.directory / "android-chrome-512x512.png") as icon:
        assert icon.size == (512, 512)
        # a wide logo is centred, leaving the top transparent
        assert icon.getpixel((256, 0))[3] == 0
        assert icon.getpixel((256, 256))[:3] == (0, 255, 0)

    with Image.open(branding.directory / "apple-touch-icon.png") as icon:
        assert icon.size == (180, 180)
        assert icon.getpixel((0, 0)) == (255, 255, 255, 255)


def test_new_logo_gets_new_version(branding_dir: Path):
    write_logo(branding_dir, color="#00FF00")
    first = BrandingService().load()

    write_logo(branding_dir, color="#0000FF")
    second = BrandingService().load()

    assert first and second
    assert first.version != second.version
    assert not first.directory.exists(), "old icons should be cleaned up"


def test_unknown_files_are_not_served(branding_dir: Path):
    write_logo(branding_dir)
    branding = BrandingService().load()

    assert branding is not None
    assert branding.get_file("../logo.png") is None
    assert branding.get_file(".complete") is None


def test_unreadable_logo_falls_back_to_default(branding_dir: Path):
    branding_dir.mkdir(parents=True)
    (branding_dir / "logo.png").write_text("not an image")

    assert get_branding() is None


def test_branding_api(api_client: TestClient, branding_dir: Path):
    response = api_client.get(api_routes.app_about)
    assert response.json()["customLogoVersion"] is None
    assert api_client.get(f"{api_routes.app_about}/branding/logo.png").status_code == 404

    get_branding.cache_clear()
    write_logo(branding_dir)

    version = api_client.get(api_routes.app_about).json()["customLogoVersion"]
    assert version

    response = api_client.get(f"{api_routes.app_about}/branding/logo.png?v={version}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    assert api_client.get(f"{api_routes.app_about}/branding/secrets.txt").status_code == 404
    assert all(icon["src"].endswith(f"?v={version}") for icon in app_icons())
