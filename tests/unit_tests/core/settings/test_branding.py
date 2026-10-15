from pathlib import Path

from pytest import MonkeyPatch

from mealie.core.settings.branding import Branding


def test_branding_defaults():
    branding = Branding()

    assert branding.name == "Mealie"
    assert branding.logo_file is None


def test_branding_env_vars(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("BRANDING_NAME", "My Recipes")

    branding = Branding()

    assert branding.name == "My Recipes"


def test_branding_logo_file_valid(tmp_path: Path):
    logo_path = tmp_path / "logo.svg"
    logo_path.write_text("<svg></svg>")

    branding = Branding(logo_path=str(logo_path))

    assert branding.logo_file == logo_path


def test_branding_logo_file_missing_path_falls_back():
    branding = Branding(logo_path="/nonexistent/path/logo.svg")
    assert branding.logo_file is None


def test_branding_logo_file_directory_falls_back(tmp_path: Path):
    branding = Branding(logo_path=str(tmp_path))
    assert branding.logo_file is None


def test_branding_logo_file_disallowed_suffix_falls_back(tmp_path: Path):
    bad_file = tmp_path / "logo.txt"
    bad_file.write_text("not an image")

    branding = Branding(logo_path=str(bad_file))
    assert branding.logo_file is None


def test_branding_logo_file_unset():
    branding = Branding(logo_path=None)
    assert branding.logo_file is None
