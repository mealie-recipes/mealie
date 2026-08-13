from pathlib import Path

from pytest import MonkeyPatch

from mealie.core.settings.branding import Branding


def test_branding_defaults():
    branding = Branding()

    assert branding.name == "Mealie"
    assert branding.html_title == "Mealie"
    assert branding.icon_file is None
    assert branding.favicon_file is None


def test_branding_env_vars(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("BRANDING_NAME", "My Recipes")
    monkeypatch.setenv("BRANDING_HTML_TITLE", "My Recipes - Home")

    branding = Branding()

    assert branding.name == "My Recipes"
    assert branding.html_title == "My Recipes - Home"


def test_branding_icon_file_valid(tmp_path: Path):
    icon_path = tmp_path / "icon.svg"
    icon_path.write_text("<svg></svg>")

    branding = Branding(icon_path=str(icon_path), favicon_path=str(icon_path))

    assert branding.icon_file == icon_path
    assert branding.favicon_file == icon_path


def test_branding_icon_file_missing_path_falls_back():
    branding = Branding(icon_path="/nonexistent/path/icon.svg")
    assert branding.icon_file is None


def test_branding_icon_file_directory_falls_back(tmp_path: Path):
    branding = Branding(icon_path=str(tmp_path))
    assert branding.icon_file is None


def test_branding_icon_file_disallowed_suffix_falls_back(tmp_path: Path):
    bad_file = tmp_path / "icon.txt"
    bad_file.write_text("not an image")

    branding = Branding(icon_path=str(bad_file))
    assert branding.icon_file is None


def test_branding_icon_file_unset():
    branding = Branding(icon_path=None)
    assert branding.icon_file is None
