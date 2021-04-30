from pathlib import Path

from mealie.core.config import CWD, DATA_DIR, AppDirectories, AppSettings, determine_data_dir, determine_secrets


def test_default_settings(monkeypatch):
    monkeypatch.delenv("DEFAULT_GROUP", raising=False)
    monkeypatch.delenv("DEFAULT_PASSWORD", raising=False)
    monkeypatch.delenv("DB_USERNAME", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    monkeypatch.delenv("DEFAULT_PASSWORD", raising=False)
    monkeypatch.delenv("API_PORT", raising=False)
    monkeypatch.delenv("API_DOCS", raising=False)
    monkeypatch.delenv("IS_DEMO", raising=False)

    app_settings = AppSettings()

    assert app_settings.DEFAULT_GROUP == "Home"
    assert app_settings.DEFAULT_PASSWORD == "MyPassword"
    assert app_settings.DB_USERNAME == "mealie"
    assert app_settings.DB_PASSWORD == "mealie"
    assert app_settings.API_PORT == 9000
    assert app_settings.API_DOCS is True
    assert app_settings.IS_DEMO is False

    assert app_settings.REDOC_URL == "/redoc"
    assert app_settings.DOCS_URL == "/docs"


def test_non_default_settings(monkeypatch):
    monkeypatch.setenv("DEFAULT_GROUP", "Test Group")
    monkeypatch.setenv("DEFAULT_PASSWORD", "Test Password")
    monkeypatch.setenv("DB_USERNAME", "mealie-test")
    monkeypatch.setenv("DB_PASSWORD", "mealie-test")
    monkeypatch.setenv("API_PORT", "8000")
    monkeypatch.setenv("API_DOCS", "False")

    app_settings = AppSettings()

    assert app_settings.DEFAULT_GROUP == "Test Group"
    assert app_settings.DEFAULT_PASSWORD == "Test Password"
    assert app_settings.DB_USERNAME == "mealie-test"
    assert app_settings.DB_PASSWORD == "mealie-test"
    assert app_settings.API_PORT == 8000
    assert app_settings.API_DOCS is False

    assert app_settings.REDOC_URL is None
    assert app_settings.DOCS_URL is None


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
