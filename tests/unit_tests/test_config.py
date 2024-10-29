import re
from dataclasses import dataclass

import pytest

from mealie.core.config import get_app_settings
from mealie.core.settings.settings import AppSettings


def test_non_default_settings(monkeypatch):
    monkeypatch.setenv("DEFAULT_GROUP", "Test Group")
    monkeypatch.setenv("DEFAULT_HOUSEHOLD", "Test Household")
    monkeypatch.setenv("API_PORT", "8000")
    monkeypatch.setenv("API_DOCS", "False")

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    assert app_settings.DEFAULT_GROUP == "Test Group"
    assert app_settings.DEFAULT_HOUSEHOLD == "Test Household"
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


psql_validation_cases = [
    (
        "unencoded_to_encoded_password",
        [
            "POSTGRES_PASSWORD",
            "P@ssword!@#$%%^^&&**()+;'\"'<>?{}[]",
            "P%40ssword%21%40%23%24%25%25%5E%5E%26%26%2A%2A%28%29%2B%3B%27%22%27%3C%3E%3F%7B%7D%5B%5D",
        ],
    ),
    (
        "unencoded_to_encoded_url",
        [
            "POSTGRES_URL_OVERRIDE",
            "postgresql://mealie:P@ssword!@#$%%^^&&**()+;'\"'<>?{}[]@postgres:5432/mealie",
            "postgresql://mealie:P%40ssword%21%40%23%24%25%25%5E%5E%26%26%2A%2A%28%29%2B%3B%27%22%27%3C%3E%3F%7B%7D%5B%5D@postgres:5432/mealie",
        ],
    ),
    (
        "no_encode_needed_password",
        [
            "POSTGRES_PASSWORD",
            "MyPassword",
            "MyPassword",
        ],
    ),
    (
        "no_encode_needed_url",
        [
            "POSTGRES_URL_OVERRIDE",
            "postgresql://mealie:MyPassword@postgres:5432/mealie",
            "postgresql://mealie:MyPassword@postgres:5432/mealie",
        ],
    ),
]

psql_cases = [x[1] for x in psql_validation_cases]
psql_cases_ids = [x[0] for x in psql_validation_cases]


@pytest.mark.parametrize("data", psql_cases, ids=psql_cases_ids)
def test_pg_connection_url_encode_password(data, monkeypatch):
    env, value, expected = data
    monkeypatch.setenv("DB_ENGINE", "postgres")
    monkeypatch.setenv(env, value)

    get_app_settings.cache_clear()
    app_settings = get_app_settings()

    pg_provider = app_settings.DB_PROVIDER
    expected = (
        expected
        if expected.startswith("postgresql://")
        else f"postgresql://{pg_provider.POSTGRES_USER}:{expected}@{pg_provider.POSTGRES_SERVER}:5432/{pg_provider.POSTGRES_DB}"
    )

    assert app_settings.DB_URL == expected


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
