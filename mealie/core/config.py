import os
from functools import lru_cache
from pathlib import Path

import dotenv

from mealie.core.settings import app_settings_constructor

from .settings import AppDirectories, AppSettings

CWD = Path(__file__).parent
BASE_DIR = CWD.parent.parent
ENV = BASE_DIR.joinpath(".env")

dotenv.load_dotenv(ENV)
PRODUCTION = os.getenv("PRODUCTION", "True").lower() in ["true", "1"]
TESTING = os.getenv("TESTING", "False").lower() in ["true", "1"]
DATA_DIR = os.getenv("DATA_DIR")
LOG_DIR = os.getenv("LOG_DIR")


def determine_data_dir() -> Path:
    global PRODUCTION, TESTING, BASE_DIR, DATA_DIR

    if TESTING:
        return BASE_DIR.joinpath(DATA_DIR if DATA_DIR else "tests/.temp")

    if PRODUCTION:
        return Path(DATA_DIR if DATA_DIR else "/app/data")

    return BASE_DIR.joinpath("dev", "data")


def determine_log_dir() -> Path:
    global PRODUCTION, TESTING, BASE_DIR, LOG_DIR

    if LOG_DIR:
        if TESTING:
            return BASE_DIR.joinpath(LOG_DIR)

        if PRODUCTION:
            return Path(LOG_DIR)

    return determine_data_dir()


@lru_cache
def get_app_dirs() -> AppDirectories:
    return AppDirectories(determine_data_dir())


@lru_cache
def get_app_settings() -> AppSettings:
    return app_settings_constructor(env_file=ENV, production=PRODUCTION, data_dir=determine_data_dir())
