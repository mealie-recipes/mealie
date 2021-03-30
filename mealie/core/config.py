import os
import secrets
from pathlib import Path

import dotenv

APP_VERSION = "v0.4.0"
DB_VERSION = "v0.4.0"

CWD = Path(__file__).parent
BASE_DIR = CWD.parent.parent

ENV = BASE_DIR.joinpath(".env") 
dotenv.load_dotenv(ENV)
PRODUCTION = os.environ.get("ENV")


def determine_data_dir(production: bool) -> Path:
    global CWD
    if production:
        return Path("/app/data")

    return CWD.parent.parent.joinpath("dev", "data")


def determine_secrets(production: bool) -> str:
    if not production:
        return "shh-secret-test-key"

    secrets_file = DATA_DIR.joinpath(".secret")
    if secrets_file.is_file():
        with open(secrets_file, "r") as f:
            return f.read()
    else:
        with open(secrets_file, "w") as f:
            new_secret = secrets.token_hex(32)
            f.write(new_secret)
        return new_secret


class AppDirectories:
    def __init__(self, cwd, data_dir) -> None:
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


class AppSettings:
    def __init__(self, app_dirs: AppDirectories) -> None:
        global DB_VERSION
        self.PRODUCTION = bool(os.environ.get("ENV"))
        self.API_PORT = int(os.getenv("API_PORT", 9000))
        self.API = bool(os.getenv("API_DOCS", True))
        self.DOCS_URL = "/docs" if self.API else None
        self.REDOC_URL = "/redoc" if self.API else None
        self.SECRET = determine_secrets(self.PRODUCTION)
        self.DATABASE_TYPE = os.getenv("DB_TYPE", "sqlite")

        # Used to Set SQLite File Version
        self.SQLITE_FILE = None
        if self.DATABASE_TYPE == "sqlite":
            self.SQLITE_FILE = app_dirs.SQLITE_DIR.joinpath(f"mealie_{DB_VERSION}.sqlite")
        else:
            raise Exception("Unable to determine database type. Acceptible options are 'sqlite' ")

        self.DEFAULT_GROUP = os.getenv("DEFAULT_GROUP", "Home")
        self.DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "MyPassword")

        # Not Used!
        self.SFTP_USERNAME = os.getenv("SFTP_USERNAME", None)
        self.SFTP_PASSWORD = os.getenv("SFTP_PASSWORD", None)


# General
DATA_DIR = determine_data_dir(PRODUCTION)
LOGGER_FILE = DATA_DIR.joinpath("mealie.log")

app_dirs = AppDirectories(CWD, DATA_DIR)
settings = AppSettings(app_dirs)
