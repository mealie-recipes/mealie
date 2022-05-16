import re

from mealie.core.config import get_app_settings


def test_non_default_settings(monkeypatch):
    monkeypatch.setenv("DEFAULT_GROUP", "Test Group")
    monkeypatch.setenv("DEFAULT_PASSWORD", "Test Password")
    monkeypatch.setenv("API_PORT", "8000")
    monkeypatch.setenv("API_DOCS", "False")

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    assert app_settings.DEFAULT_GROUP == "Test Group"
    assert app_settings.DEFAULT_PASSWORD == "Test Password"
    assert app_settings.API_PORT == 8000
    assert app_settings.API_DOCS is False

    assert app_settings.REDOC_URL is None
    assert app_settings.DOCS_URL is None


def test_default_connection_args(monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "sqlite")
    get_app_settings.cache_clear()
    app_settings = get_app_settings()
    assert re.match(r"sqlite:////.*mealie*.db", app_settings.DB_URL)


def test_pg_connection_args(monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "postgres")
    monkeypatch.setenv("POSTGRES_SERVER", "postgres")
    get_app_settings.cache_clear()
    app_settings = get_app_settings()
    assert app_settings.DB_URL == "postgresql://mealie:mealie@postgres:5432/mealie"


def test_smtp_tls_backfill(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "")
    monkeypatch.setenv("SMTP_PORT", "")
    monkeypatch.setenv("SMTP_TLS", "true")
    monkeypatch.setenv("SMTP_FROM_NAME", "")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "")
    monkeypatch.setenv("SMTP_USER", "")
    monkeypatch.setenv("SMTP_PASSWORD", "")

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    assert app_settings.SMTP_AUTH_STRATEGY == "TLS"

    monkeypatch.setenv("SMTP_HOST", "")
    monkeypatch.setenv("SMTP_PORT", "")
    monkeypatch.setenv("SMTP_TLS", "false")
    monkeypatch.setenv("SMTP_FROM_NAME", "")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "")
    monkeypatch.setenv("SMTP_USER", "")
    monkeypatch.setenv("SMTP_PASSWORD", "")
    monkeypatch.setenv("SMTP_AUTH_STRATEGY", "NONE")

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    assert app_settings.SMTP_AUTH_STRATEGY == "NONE"


def test_smtp_enable_with_bad_data_tls(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "")
    monkeypatch.setenv("SMTP_PORT", "")
    monkeypatch.setenv("SMTP_AUTH_STRATEGY", "tls")
    monkeypatch.setenv("SMTP_FROM_NAME", "")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "")
    monkeypatch.setenv("SMTP_USER", "")
    monkeypatch.setenv("SMTP_PASSWORD", "")

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    assert app_settings.SMTP_ENABLE is False


def test_smtp_enable_with_bad_data_ssl(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "")
    monkeypatch.setenv("SMTP_PORT", "")
    monkeypatch.setenv("SMTP_AUTH_STRATEGY", "ssl")
    monkeypatch.setenv("SMTP_FROM_NAME", "")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "")
    monkeypatch.setenv("SMTP_USER", "")
    monkeypatch.setenv("SMTP_PASSWORD", "")

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    assert app_settings.SMTP_ENABLE is False


def test_smtp_enable_with_no_auth(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "email.mealie.io")
    monkeypatch.setenv("SMTP_PORT", "25")
    monkeypatch.setenv("SMTP_AUTH_STRATEGY", "none")
    monkeypatch.setenv("SMTP_FROM_NAME", "Mealie")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "mealie@mealie.io")

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    assert app_settings.SMTP_ENABLE is True


def test_smtp_enable_with_tls(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "email.mealie.io")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_AUTH_STRATEGY", "tls")
    monkeypatch.setenv("SMTP_FROM_NAME", "Mealie")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "mealie@mealie.io")
    monkeypatch.setenv("SMTP_USER", "mealie@mealie.io")
    monkeypatch.setenv("SMTP_PASSWORD", "mealie-password")

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    assert app_settings.SMTP_ENABLE is True


def test_smtp_enable_with_ssl(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "email.mealie.io")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_AUTH_STRATEGY", "ssl")
    monkeypatch.setenv("SMTP_FROM_NAME", "Mealie")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "mealie@mealie.io")
    monkeypatch.setenv("SMTP_USER", "mealie@mealie.io")
    monkeypatch.setenv("SMTP_PASSWORD", "mealie-password")

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    assert app_settings.SMTP_ENABLE is True
