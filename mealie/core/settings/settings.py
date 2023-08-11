import secrets
from pathlib import Path

from pydantic import BaseSettings, NoneStr, validator

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
    PRODUCTION: bool
    BASE_URL: str = "http://localhost:8080"
    """trailing slashes are trimmed (ex. `http://localhost:8080/` becomes ``http://localhost:8080`)"""

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

    @validator("BASE_URL")
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
    DEFAULT_EMAIL: str = "changeme@email.com"
    DEFAULT_PASSWORD: str = "MyPassword"

    # ===============================================
    # Email Configuration

    SMTP_HOST: str | None
    SMTP_PORT: str | None = "587"
    SMTP_FROM_NAME: str | None = "Mealie"
    SMTP_FROM_EMAIL: str | None
    SMTP_USER: str | None
    SMTP_PASSWORD: str | None
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
        host: str | None,
        port: str | None,
        from_name: str | None,
        from_email: str | None,
        strategy: str | None,
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
    # JWT AUTH Configuration

    JWT_AUTH_ENABLED: bool = False
    JWT_AUTH_HEADER_NAME: str = "X-JWT-Assertion"
    JWT_AUTH_EMAIL_CLAIM: str = "email"
    JWT_AUTH_NAME_CLAIM: str = "name"
    JWT_AUTH_USERNAME_CLAIM: str = "user"
    JWT_AUTH_AUTO_SIGN_UP: bool = False
    JWT_AUTH_JWK_SET_URL: str = "https://your-auth-provider.example.com/.well-known/jwks.json"

    # ===============================================
    # LDAP Configuration

    LDAP_AUTH_ENABLED: bool = False
    LDAP_SERVER_URL: NoneStr = None
    LDAP_TLS_INSECURE: bool = False
    LDAP_TLS_CACERTFILE: NoneStr = None
    LDAP_ENABLE_STARTTLS: bool = False
    LDAP_BASE_DN: NoneStr = None
    LDAP_QUERY_BIND: NoneStr = None
    LDAP_QUERY_PASSWORD: NoneStr = None
    LDAP_USER_FILTER: NoneStr = None
    LDAP_ADMIN_FILTER: NoneStr = None
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
