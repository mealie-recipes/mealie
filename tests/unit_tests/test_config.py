from pathlib import Path

import pytest
from mealie.core.config import CWD, DATA_DIR, AppDirectories, AppSettings, determine_data_dir, determine_secrets


def test_non_default_settings(monkeypatch):
    monkeypatch.setenv("DEFAULT_GROUP", "Test Group")
    monkeypatch.setenv("DEFAULT_PASSWORD", "Test Password")
    monkeypatch.setenv("API_PORT", "8000")
    monkeypatch.setenv("API_DOCS", False)

    app_dirs = AppDirectories(CWD, DATA_DIR)
    app_settings = AppSettings(app_dirs)

    assert app_settings.DEFAULT_GROUP == "Test Group"
    assert app_settings.DEFAULT_PASSWORD == "Test Password"
    assert app_settings.API_PORT == 8000
    assert app_settings.API is False

    assert app_settings.REDOC_URL is None
    assert app_settings.DOCS_URL is None


def test_unknown_database(monkeypatch):
    monkeypatch.setenv("DB_TYPE", "nonsense")

    with pytest.raises(Exception, match="Unable to determine database type. Acceptible options are 'sqlite'"):
        app_dirs = AppDirectories(CWD, DATA_DIR)
        AppSettings(app_dirs)


def test_secret_generation(tmp_path):
    app_dirs = AppDirectories(CWD, DATA_DIR)
    assert determine_secrets(app_dirs.DATA_DIR, False) == "shh-secret-test-key"
    assert determine_secrets(app_dirs.DATA_DIR, True) != "shh-secret-test-key"

    assert determine_secrets(tmp_path, True) != "shh-secret-test-key"


def test_set_data_dir():
    global CWD
    PROD_DIR = Path("/app/data")
    DEV_DIR = CWD.parent.parent.joinpath("dev", "data")

    assert determine_data_dir(True) == PROD_DIR
    assert determine_data_dir(False) == DEV_DIR
