import re
from dataclasses import dataclass

import pytest

from mealie.core.config import get_app_settings
from mealie.core.settings.settings import AppSettings


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


@dataclass(slots=True)
class SMTPValidationCase:
    host: str
    port: str
    auth_strategy: str
    from_name: str
    from_email: str
    user: str
    password: str
    is_valid: bool


smtp_validation_cases = [
    (
        "bad_data_tls",
        SMTPValidationCase("", "", "tls", "", "", "", "", False),
    ),
    (
        "bad_data_ssl",
        SMTPValidationCase("", "", "ssl", "", "", "", "", False),
    ),
    (
        "no_auth",
        SMTPValidationCase("email.mealie.io", "25", "none", "Mealie", "mealie@mealie.io", "", "", True),
    ),
    (
        "good_data_tls",
        SMTPValidationCase(
            "email.mealie.io", "587", "tls", "Mealie", "mealie@mealie.io", "mealie@mealie.io", "mealie-password", True
        ),
    ),
    (
        "good_data_ssl",
        SMTPValidationCase(
            "email.mealie.io", "465", "tls", "Mealie", "mealie@mealie.io", "mealie@mealie.io", "mealie-password", True
        ),
    ),
]

smtp_cases = [x[1] for x in smtp_validation_cases]
smtp_cases_ids = [x[0] for x in smtp_validation_cases]


@pytest.mark.parametrize("data", smtp_cases, ids=smtp_cases_ids)
def test_smtp_enable_with_bad_data_tls(data: SMTPValidationCase):
    is_valid = AppSettings.validate_smtp(
        data.host,
        data.port,
        data.from_name,
        data.from_email,
        data.auth_strategy,
        data.user,
        data.password,
    )

    assert is_valid is data.is_valid
