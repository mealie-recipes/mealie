import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional, Union

import dotenv
from pydantic import BaseSettings, Field, PostgresDsn, validator

APP_VERSION = "v0.5.2"
DB_VERSION = "v0.5.0"

CWD = Path(__file__).parent
BASE_DIR = CWD.parent.parent

ENV = BASE_DIR.joinpath(".env")

dotenv.load_dotenv(ENV)
PRODUCTION = os.getenv("PRODUCTION", "True").lower() in ["true", "1"]


def determine_data_dir(production: bool) -> Path:
    global CWD
    if production:
        return Path("/app/data")

    return CWD.parent.parent.joinpath("dev", "data")


def determine_secrets(data_dir: Path, production: bool) -> str:
    if not production:
        return "shh-secret-test-key"

    secrets_file = data_dir.joinpath(".secret")
    if secrets_file.is_file():
        with open(secrets_file, "r") as f:
            return f.read()
    else:
        with open(secrets_file, "w") as f:
            new_secret = secrets.token_hex(32)
            f.write(new_secret)
        return new_secret


# General
DATA_DIR = determine_data_dir(PRODUCTION)


class AppDirectories:
    def __init__(self, cwd, data_dir) -> None:
        self.DATA_DIR: Path = data_dir
        self.WEB_PATH: Path = cwd.joinpath("dist")
        self.IMG_DIR: Path = data_dir.joinpath("img")
        self.BACKUP_DIR: Path = data_dir.joinpath("backups")
        self.DEBUG_DIR: Path = data_dir.joinpath("debug")
        self.MIGRATION_DIR: Path = data_dir.joinpath("migration")
        self.NEXTCLOUD_DIR: Path = self.MIGRATION_DIR.joinpath("nextcloud")
        self.CHOWDOWN_DIR: Path = self.MIGRATION_DIR.joinpath("chowdown")
        self.TEMPLATE_DIR: Path = data_dir.joinpath("templates")
        self.USER_DIR: Path = data_dir.joinpath("users")
        self.RECIPE_DATA_DIR: Path = data_dir.joinpath("recipes")
        self.TEMP_DIR: Path = data_dir.joinpath(".temp")

        self.ensure_directories()

    def ensure_directories(self):
        required_dirs = [
            self.IMG_DIR,
            self.BACKUP_DIR,
            self.DEBUG_DIR,
            self.MIGRATION_DIR,
            self.TEMPLATE_DIR,
            self.NEXTCLOUD_DIR,
            self.CHOWDOWN_DIR,
            self.RECIPE_DATA_DIR,
            self.USER_DIR,
        ]

        for dir in required_dirs:
            dir.mkdir(parents=True, exist_ok=True)


app_dirs = AppDirectories(CWD, DATA_DIR)


def determine_sqlite_path(path=False, suffix=DB_VERSION) -> str:
    global app_dirs
    db_path = app_dirs.DATA_DIR.joinpath(f"mealie_{suffix}.db")  # ! Temporary Until Alembic

    if path:
        return db_path

    return "sqlite:///" + str(db_path.absolute())


class AppSettings(BaseSettings):
    global DATA_DIR
    PRODUCTION: bool = Field(True, env="PRODUCTION")
    BASE_URL: str = "http://localhost:8080"
    IS_DEMO: bool = False
    API_PORT: int = 9000
    API_DOCS: bool = True

    @property
    def DOCS_URL(self) -> str:
        return "/docs" if self.API_DOCS else None

    @property
    def REDOC_URL(self) -> str:
        return "/redoc" if self.API_DOCS else None

    SECRET: str = determine_secrets(DATA_DIR, PRODUCTION)

    DB_ENGINE: str = "sqlite"  # Optional: 'sqlite', 'postgres'
    POSTGRES_USER: str = "mealie"
    POSTGRES_PASSWORD: str = "mealie"
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: str = 5432
    POSTGRES_DB: str = "mealie"

    DB_URL: Union[str, PostgresDsn] = None  # Actual DB_URL is calculated with `assemble_db_connection`

    @validator("DB_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        engine = values.get("DB_ENGINE", "sqlite")
        if engine == "postgres":
            host = f"{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}"
            return PostgresDsn.build(
                scheme="postgresql",
                user=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=host,
                path=f"/{values.get('POSTGRES_DB') or ''}",
            )
        return determine_sqlite_path()

    DB_URL_PUBLIC: str = ""  # hide credentials to show on logs/frontend

    @validator("DB_URL_PUBLIC", pre=True)
    def public_db_url(cls, v: Optional[str], values: dict[str, Any]) -> str:
        url = values.get("DB_URL")
        engine = values.get("DB_ENGINE", "sqlite")
        if engine != "postgres":
            # sqlite
            return url

        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        return url.replace(user, "*****", 1).replace(password, "*****", 1)

    DEFAULT_GROUP: str = "Home"
    DEFAULT_EMAIL: str = "changeme@email.com"
    DEFAULT_PASSWORD: str = "MyPassword"

    SCHEDULER_DATABASE = f"sqlite:///{app_dirs.DATA_DIR.joinpath('scheduler.db')}"

    TOKEN_TIME: int = 2  # Time in Hours

    # Not Used!
    SFTP_USERNAME: Optional[str]
    SFTP_PASSWORD: Optional[str]

    # Recipe Default Settings
    RECIPE_PUBLIC: bool = True
    RECIPE_SHOW_NUTRITION: bool = True
    RECIPE_SHOW_ASSETS: bool = True
    RECIPE_LANDSCAPE_VIEW: bool = True
    RECIPE_DISABLE_COMMENTS: bool = False
    RECIPE_DISABLE_AMOUNT: bool = False

    class Config:
        env_file = BASE_DIR.joinpath(".env")
        env_file_encoding = "utf-8"


settings = AppSettings()


@lru_cache
def get_app_dirs() -> AppDirectories:
    global app_dirs
    return app_dirs


@lru_cache
def get_settings() -> AppSettings:
    global settings
    return settings
