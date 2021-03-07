import os
from pathlib import Path

import dotenv

CWD = Path(__file__).parent


def ensure_dirs():
    for dir in REQUIRED_DIRS:
        dir.mkdir(parents=True, exist_ok=True)


# Register ENV
ENV = CWD.joinpath(".env")  #! I'm Broken Fix Me!
dotenv.load_dotenv(ENV)


SECRET = "super-secret-key"

# General
APP_VERSION = "v0.3.0"
DB_VERSION = "v0.3.0"
PRODUCTION = os.environ.get("ENV")
PORT = int(os.getenv("mealie_port", 9000))
API = os.getenv("api_docs", True)

if API:
    docs_url = "/docs"
    redoc_url = "/redoc"
else:
    docs_url = None
    redoc_url = None

# Helpful Globals
DATA_DIR = CWD.parent.parent.joinpath("app_data")
if PRODUCTION:
    DATA_DIR = Path("/app/data")

WEB_PATH = CWD.joinpath("dist")
IMG_DIR = DATA_DIR.joinpath("img")
BACKUP_DIR = DATA_DIR.joinpath("backups")
DEBUG_DIR = DATA_DIR.joinpath("debug")
MIGRATION_DIR = DATA_DIR.joinpath("migration")
NEXTCLOUD_DIR = MIGRATION_DIR.joinpath("nextcloud")
CHOWDOWN_DIR = MIGRATION_DIR.joinpath("chowdown")
TEMPLATE_DIR = DATA_DIR.joinpath("templates")
USER_DIR = DATA_DIR.joinpath("users")
SQLITE_DIR = DATA_DIR.joinpath("db")
RECIPE_DATA_DIR = DATA_DIR.joinpath("recipes")
TEMP_DIR = DATA_DIR.joinpath(".temp")

REQUIRED_DIRS = [
    DATA_DIR,
    IMG_DIR,
    BACKUP_DIR,
    DEBUG_DIR,
    MIGRATION_DIR,
    TEMPLATE_DIR,
    SQLITE_DIR,
    NEXTCLOUD_DIR,
    CHOWDOWN_DIR,
    RECIPE_DATA_DIR,
    USER_DIR,
]

ensure_dirs()

LOGGER_FILE = DATA_DIR.joinpath("mealie.log")


# DATABASE ENV
SQLITE_FILE = None
DATABASE_TYPE = os.getenv("db_type", "sqlite")
if DATABASE_TYPE == "sqlite":
    USE_SQL = True
    SQLITE_FILE = SQLITE_DIR.joinpath(f"mealie_{DB_VERSION}.sqlite")

else:
    raise Exception(
        "Unable to determine database type. Acceptible options are 'sqlite' "
    )

# Mongo Database
MEALIE_DB_NAME = os.getenv("mealie_db_name", "mealie")
DEFAULT_GROUP = os.getenv("default_group", "home")
DB_USERNAME = os.getenv("db_username", "root")
DB_PASSWORD = os.getenv("db_password", "example")
DB_HOST = os.getenv("db_host", "mongo")
DB_PORT = os.getenv("db_port", 27017)

# SFTP Email Stuff - For use Later down the line!
SFTP_USERNAME = os.getenv("sftp_username", None)
SFTP_PASSWORD = os.getenv("sftp_password", None)
