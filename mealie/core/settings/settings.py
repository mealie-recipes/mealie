import secrets
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings

from .db_providers import AbstractDBProvider, db_provider_factory


def determine_secrets(data_dir: Path, production: bool) -> str:
    if not production:
        return "shh-secret-test-key"

    secrets_file = data_dir.joinpath(".secret")
    if secrets_file.is_file():
        with open(secrets_file, "r") as f:
            return f.read()
    else:
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(secrets_file, "w") as f:
            new_secret = secrets.token_hex(32)
            f.write(new_secret)
        return new_secret


class AppSettings(BaseSettings):
    PRODUCTION: bool
    BASE_URL: str = "http://localhost:8080"
    IS_DEMO: bool = False
    API_PORT: int = 9000
    API_DOCS: bool = True
    TOKEN_TIME: int = 48  # Time in Hours
    SECRET: str

    @property
    def DOCS_URL(self) -> str:
        return "/docs" if self.API_DOCS else None

    @property
    def REDOC_URL(self) -> str:
        return "/redoc" if self.API_DOCS else None

    # ===============================================
    # Database Configuration

    DB_ENGINE: str = "sqlite"  # Options: 'sqlite', 'postgres'
    DB_PROVIDER: AbstractDBProvider = None

    @property
    def DB_URL(self) -> str:
        return self.DB_PROVIDER.db_url

    @property
    def DB_URL_PUBLIC(self) -> str:
        return self.DB_PROVIDER.db_url_public

    DEFAULT_GROUP: str = "Home"
    DEFAULT_EMAIL: str = "changeme@email.com"
    DEFAULT_PASSWORD: str = "MyPassword"

    # ===============================================
    # Email Configuration

    SMTP_HOST: Optional[str]
    SMTP_PORT: Optional[str] = "587"
    SMTP_FROM_NAME: Optional[str] = "Mealie"
    SMTP_TLS: Optional[bool] = True
    SMTP_FROM_EMAIL: Optional[str]
    SMTP_USER: Optional[str]
    SMTP_PASSWORD: Optional[str]

    @property
    def SMTP_ENABLE(self) -> bool:
        """Validates all SMTP variables are set"""
        required = {
            self.SMTP_HOST,
            self.SMTP_PORT,
            self.SMTP_FROM_NAME,
            self.SMTP_TLS,
            self.SMTP_FROM_EMAIL,
            self.SMTP_USER,
            self.SMTP_PASSWORD,
        }

        return "" not in required and None not in required

    # ===============================================
    # LDAP Configuration

    LDAP_AUTH_ENABLED: bool = False
    LDAP_SERVER_URL: str = None
    LDAP_BIND_TEMPLATE: str = None
    LDAP_ADMIN_FILTER: str = None

    @property
    def LDAP_ENABLED(self) -> bool:
        """Validates LDAP settings are all set"""
        required = {
            self.LDAP_SERVER_URL,
            self.LDAP_BIND_TEMPLATE,
            self.LDAP_ADMIN_FILTER,
        }
        not_none = None not in required
        return self.LDAP_AUTH_ENABLED and not_none

    # ===============================================
    # Testing Config

    TESTING: bool = False

    class Config:
        arbitrary_types_allowed = True


def app_settings_constructor(data_dir: Path, production: bool, env_file: Path, env_encoding="utf-8") -> AppSettings:
    """
    app_settings_constructor is a factory function that returns an AppSettings object. It is used to inject the
    required dependencies into the AppSettings object and nested child objects. AppSettings should not be substantiated
    directly, but rather through this factory function.
    """
    app_settings = AppSettings(
        _env_file=env_file,
        _env_file_encoding=env_encoding,
        **{"SECRET": determine_secrets(data_dir, production)},
    )

    app_settings.DB_PROVIDER = db_provider_factory(
        app_settings.DB_ENGINE or "sqlite",
        data_dir,
        env_file=env_file,
        env_encoding=env_encoding,
    )

    return app_settings
