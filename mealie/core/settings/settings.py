import secrets
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from mealie.core.settings.themes import Theme

from .db_providers import AbstractDBProvider, db_provider_factory


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


class AppSettings(BaseSettings):
    theme: Theme = Theme()

    PRODUCTION: bool
    BASE_URL: str = "http://localhost:8080"
    """trailing slashes are trimmed (ex. `http://localhost:8080/` becomes ``http://localhost:8080`)"""

    STATIC_FILES: str = ""
    """path to static files directory (ex. `mealie/dist`)"""

    IS_DEMO: bool = False
    API_PORT: int = 9000
    API_DOCS: bool = True
    TOKEN_TIME: int = 48
    """time in hours"""

    SECRET: str
    LOG_LEVEL: str = "INFO"
    """corresponds to standard Python log levels"""

    GIT_COMMIT_HASH: str = "unknown"

    ALLOW_SIGNUP: bool = True

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

    @property
    def OIDC_READY(self) -> bool:
        """Validates OIDC settings are all set"""

        required = {self.OIDC_CLIENT_ID, self.OIDC_CONFIGURATION_URL}
        not_none = None not in required
        return self.OIDC_AUTH_ENABLED and not_none

    # ===============================================
    # Testing Config

    TESTING: bool = False
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
        **{"SECRET": determine_secrets(data_dir, production)},
    )

    app_settings.DB_PROVIDER = db_provider_factory(
        app_settings.DB_ENGINE or "sqlite",
        data_dir,
        env_file=env_file,
        env_encoding=env_encoding,
    )

    return app_settings
