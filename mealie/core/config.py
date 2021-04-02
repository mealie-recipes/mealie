import os
import secrets
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseSettings, Field, validator

APP_VERSION = "v0.4.0"
DB_VERSION = "v0.4.0"

CWD = Path(__file__).parent
BASE_DIR = CWD.parent.parent

ENV = BASE_DIR.joinpath(".env")
PRODUCTION = os.getenv("ENV", 'False').lower() in ['true', '1']


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
LOGGER_FILE = DATA_DIR.joinpath("mealie.log")


class AppDirectories:
    def __init__(self, cwd, data_dir) -> None:
        self.DATA_DIR = data_dir
        self.WEB_PATH = cwd.joinpath("dist")
        self.IMG_DIR = data_dir.joinpath("img")
        self.BACKUP_DIR = data_dir.joinpath("backups")
        self.DEBUG_DIR = data_dir.joinpath("debug")
        self.MIGRATION_DIR = data_dir.joinpath("migration")
        self.NEXTCLOUD_DIR = self.MIGRATION_DIR.joinpath("nextcloud")
        self.CHOWDOWN_DIR = self.MIGRATION_DIR.joinpath("chowdown")
        self.TEMPLATE_DIR = data_dir.joinpath("templates")
        self.USER_DIR = data_dir.joinpath("users")
        self.SQLITE_DIR = data_dir.joinpath("db")
        self.RECIPE_DATA_DIR = data_dir.joinpath("recipes")
        self.TEMP_DIR = data_dir.joinpath(".temp")

        self.ensure_directories()

    def ensure_directories(self):
        required_dirs = [
            self.IMG_DIR,
            self.BACKUP_DIR,
            self.DEBUG_DIR,
            self.MIGRATION_DIR,
            self.TEMPLATE_DIR,
            self.SQLITE_DIR,
            self.NEXTCLOUD_DIR,
            self.CHOWDOWN_DIR,
            self.RECIPE_DATA_DIR,
            self.USER_DIR,
        ]

        for dir in required_dirs:
            dir.mkdir(parents=True, exist_ok=True)


app_dirs = AppDirectories(CWD, DATA_DIR)


class AppSettings(BaseSettings):
    global DATA_DIR
    PRODUCTION: bool = Field(False, env="ENV")
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
    DATABASE_TYPE: str = Field("sqlite", env="DB_TYPE")

    @validator("DATABASE_TYPE", pre=True)
    def validate_db_type(cls, v: str) -> Optional[str]:
        if v != "sqlite":
            raise ValueError("Unable to determine database type. Acceptible options are 'sqlite'")
        else:
            return v

    # Used to Set SQLite File Version
    SQLITE_FILE: Optional[Union[str, Path]]

    @validator("SQLITE_FILE", pre=True)
    def identify_sqlite_file(cls, v: str) -> Optional[str]:
        return app_dirs.SQLITE_DIR.joinpath(f"mealie_{DB_VERSION}.sqlite")

    DEFAULT_GROUP: str = "Home"
    DEFAULT_PASSWORD: str = "MyPassword"

    # Not Used!
    SFTP_USERNAME: Optional[str]
    SFTP_PASSWORD: Optional[str]

    class Config:
        env_file = BASE_DIR.joinpath(".env")
        env_file_encoding = "utf-8"


settings = AppSettings()
