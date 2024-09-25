import logging
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple

from dateutil.tz import tzlocal
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from mealie.core.settings.themes import Theme

from .db_providers import AbstractDBProvider, db_provider_factory


class ScheduleTime(NamedTuple):
    hour: int
    minute: int


def determine_secrets(data_dir: Path, production: bool) -> str:
    if not production:
        return "shh-secret-test-key"

    secrets_file = data_dir.joinpath(".secret")
    if secrets_file.is_file():
        with open(secrets_file) as f:
            return f.read()
    else:
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(secrets_file, "w") as f:
            new_secret = secrets.token_hex(32)
            f.write(new_secret)
        return new_secret


def get_secrets_dir() -> str | None:
    """
    Returns a directory to load secret settings from, or `None` if the secrets
    directory does not exist or cannot be accessed.
    """
    # Avoid a circular import by importing here instead of at the file's top-level.
    # get_logger -> AppSettings -> get_logger
    from mealie.core.root_logger import get_logger

    logger = get_logger()

    secrets_dir = "/run/secrets"

    # Check that the secrets directory exists.
    if not os.path.exists(secrets_dir):
        logger.warning(f"Secrets directory '{secrets_dir}' does not exist")
        return None

    # Likewise, check we have permission to read from the secrets directory.
    if not os.access(secrets_dir, os.R_OK):
        logger.warning(f"Secrets directory '{secrets_dir}' cannot be read from. Check permissions")
        return None

    # The secrets directory exists and can be accessed.
    return secrets_dir


class AppLoggingSettings(BaseSettings):
    """
    Subset of AppSettings to only access logging-related settings.

    This is separated out from AppSettings to allow logging during construction
    of AppSettings.
    """

    TESTING: bool = False
    PRODUCTION: bool

    LOG_CONFIG_OVERRIDE: Path | None = None
    """path to custom logging configuration file"""

    LOG_LEVEL: str = "info"
    """corresponds to standard Python log levels"""


class AppSettings(AppLoggingSettings):
    theme: Theme = Theme()

    BASE_URL: str = "http://localhost:8080"
    """trailing slashes are trimmed (ex. `http://localhost:8080/` becomes ``http://localhost:8080`)"""

    STATIC_FILES: str = ""
    """path to static files directory (ex. `mealie/dist`)"""

    IS_DEMO: bool = False

    HOST_IP: str = "*"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 9000
    API_DOCS: bool = True
    TOKEN_TIME: int = 48
    """time in hours"""

    SECRET: str

    GIT_COMMIT_HASH: str = "unknown"

    ALLOW_SIGNUP: bool = False

    DAILY_SCHEDULE_TIME: str = "23:45"
    """Local server time, in HH:MM format. See `DAILY_SCHEDULE_TIME_UTC` for the parsed UTC equivalent"""

    @property
    def logger(self) -> logging.Logger:
        # Avoid a circular import by importing here instead of at the file's top-level.
        # get_logger -> AppSettings -> get_logger
        from mealie.core.root_logger import get_logger

        return get_logger()

    @property
    def DAILY_SCHEDULE_TIME_UTC(self) -> ScheduleTime:
        """The DAILY_SCHEDULE_TIME in UTC, parsed into hours and minutes"""

        # parse DAILY_SCHEDULE_TIME into hours and minutes
        try:
            hour_str, minute_str = self.DAILY_SCHEDULE_TIME.split(":")
            local_hour = int(hour_str)
            local_minute = int(minute_str)
        except ValueError:
            local_hour = 23
            local_minute = 45
            self.logger.exception(
                f"Unable to parse {self.DAILY_SCHEDULE_TIME=} as HH:MM; defaulting to {local_hour}:{local_minute}"
            )

        # DAILY_SCHEDULE_TIME is in local time, so we convert it to UTC
        local_tz = tzlocal()
        now = datetime.now(local_tz)
        local_time = now.replace(hour=local_hour, minute=local_minute)
        utc_time = local_time.astimezone(timezone.utc)

        self.logger.debug(f"Local time: {local_hour}:{local_minute} | UTC time: {utc_time.hour}:{utc_time.minute}")
        return ScheduleTime(utc_time.hour, utc_time.minute)

    # ===============================================
    # Security Configuration

    SECURITY_MAX_LOGIN_ATTEMPTS: int = 5
    SECURITY_USER_LOCKOUT_TIME: int = 24
    "time in hours"

    @field_validator("BASE_URL")
    @classmethod
    def remove_trailing_slash(cls, v: str) -> str:
        if v and v[-1] == "/":
            return v[:-1]

        return v

    @property
    def DOCS_URL(self) -> str | None:
        return "/docs" if self.API_DOCS else None

    @property
    def REDOC_URL(self) -> str | None:
        return "/redoc" if self.API_DOCS else None

    # ===============================================
    # Database Configuration

    DB_ENGINE: str = "sqlite"  # Options: 'sqlite', 'postgres'
    DB_PROVIDER: AbstractDBProvider | None = None

    @property
    def DB_URL(self) -> str | None:
        return self.DB_PROVIDER.db_url if self.DB_PROVIDER else None

    @property
    def DB_URL_PUBLIC(self) -> str | None:
        return self.DB_PROVIDER.db_url_public if self.DB_PROVIDER else None

    DEFAULT_GROUP: str = "Home"
    DEFAULT_HOUSEHOLD: str = "Family"

    _DEFAULT_EMAIL: str = "changeme@example.com"
    """
    This is the default email used for the first user created in the database. This is only used if no users
    exist in the database. it should no longer be set by end users.
    """
    _DEFAULT_PASSWORD: str = "MyPassword"
    """
    This is the default password used for the first user created in the database. This is only used if no users
    exist in the database. it should no longer be set by end users.
    """

    # ===============================================
    # Email Configuration

    SMTP_HOST: str | None = None
    SMTP_PORT: str | None = "587"
    SMTP_FROM_NAME: str | None = "Mealie"
    SMTP_FROM_EMAIL: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_AUTH_STRATEGY: str | None = "TLS"  # Options: 'TLS', 'SSL', 'NONE'

    @property
    def SMTP_ENABLE(self) -> bool:
        return AppSettings.validate_smtp(
            self.SMTP_HOST,
            self.SMTP_PORT,
            self.SMTP_FROM_NAME,
            self.SMTP_FROM_EMAIL,
            self.SMTP_AUTH_STRATEGY,
            self.SMTP_USER,
            self.SMTP_PASSWORD,
        )

    @staticmethod
    def validate_smtp(
        host: str | None = None,
        port: str | None = None,
        from_name: str | None = None,
        from_email: str | None = None,
        strategy: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> bool:
        """Validates all SMTP variables are set"""
        required = {host, port, from_name, from_email, strategy}

        if strategy and strategy.upper() in {"TLS", "SSL"}:
            required.add(user)
            required.add(password)

        return "" not in required and None not in required

    # ===============================================
    # LDAP Configuration

    LDAP_AUTH_ENABLED: bool = False
    LDAP_SERVER_URL: str | None = None
    LDAP_TLS_INSECURE: bool = False
    LDAP_TLS_CACERTFILE: str | None = None
    LDAP_ENABLE_STARTTLS: bool = False
    LDAP_BASE_DN: str | None = None
    LDAP_QUERY_BIND: str | None = None
    LDAP_QUERY_PASSWORD: str | None = None
    LDAP_USER_FILTER: str | None = None
    LDAP_ADMIN_FILTER: str | None = None
    LDAP_ID_ATTRIBUTE: str = "uid"
    LDAP_MAIL_ATTRIBUTE: str = "mail"
    LDAP_NAME_ATTRIBUTE: str = "name"

    @property
    def LDAP_ENABLED(self) -> bool:
        """Validates LDAP settings are all set"""
        required = {
            self.LDAP_SERVER_URL,
            self.LDAP_BASE_DN,
            self.LDAP_ID_ATTRIBUTE,
            self.LDAP_MAIL_ATTRIBUTE,
            self.LDAP_NAME_ATTRIBUTE,
        }
        not_none = None not in required
        return self.LDAP_AUTH_ENABLED and not_none

    # ===============================================
    # OIDC Configuration
    OIDC_AUTH_ENABLED: bool = False
    OIDC_CLIENT_ID: str | None = None
    OIDC_CONFIGURATION_URL: str | None = None
    OIDC_SIGNUP_ENABLED: bool = True
    OIDC_USER_GROUP: str | None = None
    OIDC_ADMIN_GROUP: str | None = None
    OIDC_AUTO_REDIRECT: bool = False
    OIDC_PROVIDER_NAME: str = "OAuth"
    OIDC_REMEMBER_ME: bool = False
    OIDC_SIGNING_ALGORITHM: str = "RS256"
    OIDC_USER_CLAIM: str = "email"
    OIDC_GROUPS_CLAIM: str | None = "groups"
    OIDC_TLS_CACERTFILE: str | None = None

    @property
    def OIDC_READY(self) -> bool:
        """Validates OIDC settings are all set"""

        required = {
            self.OIDC_CLIENT_ID,
            self.OIDC_CONFIGURATION_URL,
            self.OIDC_USER_CLAIM,
        }
        not_none = None not in required
        valid_group_claim = True
        if (not self.OIDC_USER_GROUP or not self.OIDC_ADMIN_GROUP) and not self.OIDC_GROUPS_CLAIM:
            valid_group_claim = False

        return self.OIDC_AUTH_ENABLED and not_none and valid_group_claim

    # ===============================================
    # OpenAI Configuration

    OPENAI_BASE_URL: str | None = None
    """The base URL for the OpenAI API. Leave this unset for most usecases"""
    OPENAI_API_KEY: str | None = None
    """Your OpenAI API key. Required to enable OpenAI features"""
    OPENAI_MODEL: str = "gpt-4o"
    """Which OpenAI model to send requests to. Leave this unset for most usecases"""
    OPENAI_CUSTOM_HEADERS: dict[str, str] = {}
    """Custom HTTP headers to send with each OpenAI request"""
    OPENAI_CUSTOM_PARAMS: dict[str, Any] = {}
    """Custom HTTP parameters to send with each OpenAI request"""
    OPENAI_ENABLE_IMAGE_SERVICES: bool = True
    """Whether to enable image-related features in OpenAI"""
    OPENAI_WORKERS: int = 2
    """
    Number of OpenAI workers per request. Higher values may increase
    processing speed, but will incur additional API costs
    """
    OPENAI_SEND_DATABASE_DATA: bool = True
    """
    Sending database data may increase accuracy in certain requests,
    but will incur additional API costs
    """
    OPENAI_REQUEST_TIMEOUT: int = 60
    """
    The number of seconds to wait for an OpenAI request to complete before cancelling the request
    """

    # ===============================================
    # Web Concurrency

    WORKER_PER_CORE: int = 1
    """Old gunicorn env for workers per core."""

    UVICORN_WORKERS: int = 1
    """Number of Uvicorn workers to run."""

    @property
    def WORKERS(self) -> int:
        return max(1, self.WORKER_PER_CORE * self.UVICORN_WORKERS)

    @property
    def OPENAI_ENABLED(self) -> bool:
        """Validates OpenAI settings are all set"""
        return bool(self.OPENAI_API_KEY and self.OPENAI_MODEL)

    model_config = SettingsConfigDict(arbitrary_types_allowed=True, extra="allow")


def app_settings_constructor(data_dir: Path, production: bool, env_file: Path, env_encoding="utf-8") -> AppSettings:
    """
    app_settings_constructor is a factory function that returns an AppSettings object. It is used to inject the
    required dependencies into the AppSettings object and nested child objects. AppSettings should not be substantiated
    directly, but rather through this factory function.
    """
    app_settings = AppSettings(
        _env_file=env_file,  # type: ignore
        _env_file_encoding=env_encoding,  # type: ignore
        # `get_secrets_dir` must be called here rather than within `AppSettings`
        # to avoid a circular import.
        _secrets_dir=get_secrets_dir(),  # type: ignore
        **{"SECRET": determine_secrets(data_dir, production)},
    )

    app_settings.DB_PROVIDER = db_provider_factory(
        app_settings.DB_ENGINE or "sqlite",
        data_dir,
        env_file=env_file,
        env_encoding=env_encoding,
    )

    return app_settings
