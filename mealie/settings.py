import os
from pathlib import Path

import dotenv

CWD = Path(__file__).parent

# Register ENV
ENV = CWD.joinpath(".env")
dotenv.load_dotenv(ENV)

# Helpful Globals
DATA_DIR = CWD.joinpath("data")
WEB_PATH = CWD.joinpath("dist")
IMG_DIR = DATA_DIR.joinpath("img")
BACKUP_DIR = DATA_DIR.joinpath("backups")
DEBUG_DIR = DATA_DIR.joinpath("debug")
MIGRATION_DIR = DATA_DIR.joinpath("migration")
TEMPLATE_DIR = DATA_DIR.joinpath("templates")
TEMP_DIR = DATA_DIR.joinpath("temp")


# General
PRODUCTION = os.environ.get("ENV")
PORT = int(os.getenv("mealie_port", 9000))
API = os.getenv("api_docs", True)

if API:
    docs_url = "/docs"
    redoc_url = "/redoc"
else:
    docs_url = None
    redoc_url = None


# DATABASE ENV
DATABASE_TYPE = os.getenv("db_type", "mongo")  # mongo, sqlite
SQLITE = False
MONGO = False
if DATABASE_TYPE == "sqlite":
    SQLITE = True
    SQLITE_DB_FILE = DATA_DIR.joinpath("mealie.sqlite")
elif DATABASE_TYPE == "mongo":
    MONGO = True
else:
    raise Exception(
        "Unable to determine database type. Acceptible options are 'mongo' or 'sqlite' "
    )

# Mongo Database
MEALIE_DB_NAME = os.getenv("mealie_db_name", "mealie")
DB_USERNAME = os.getenv("db_username", "root")
DB_PASSWORD = os.getenv("db_password", "example")
DB_HOST = os.getenv("db_host", "mongo")
DB_PORT = os.getenv("db_port", 27017)

# SFTP Email Stuff - For use Later down the line!
SFTP_USERNAME = os.getenv("sftp_username", None)
SFTP_PASSWORD = os.getenv("sftp_password", None)
