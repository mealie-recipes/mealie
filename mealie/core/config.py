import os
from functools import lru_cache
from pathlib import Path

import dotenv

from mealie.core.settings import app_settings_constructor

from .settings import AppDirectories, AppSettings
from .settings.static import APP_VERSION, DB_VERSION

APP_VERSION
DB_VERSION

CWD = Path(__file__).parent
BASE_DIR = CWD.parent.parent
ENV = BASE_DIR.joinpath(".env")

dotenv.load_dotenv(ENV)
PRODUCTION = os.getenv("PRODUCTION", "True").lower() in ["true", "1"]
TESTING = os.getenv("TESTING", "True").lower() in ["true", "1"]


def determine_data_dir() -> Path:
    global PRODUCTION, TESTING, BASE_DIR

    if TESTING:
        return BASE_DIR.joinpath("tests/.temp")

    if PRODUCTION:
        return Path("/app/data")

    return BASE_DIR.joinpath("dev", "data")


@lru_cache
def get_app_dirs() -> AppDirectories:
    return AppDirectories(determine_data_dir())


@lru_cache
def get_app_settings() -> AppSettings:
    return app_settings_constructor(env_file=ENV, production=PRODUCTION, data_dir=determine_data_dir())
