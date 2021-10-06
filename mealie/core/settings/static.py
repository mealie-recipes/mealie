import os
from pathlib import Path

import dotenv

APP_VERSION = "v1.0.0b"
DB_VERSION = "v1.0.0b"

CWD = Path(__file__).parent
BASE_DIR = CWD.parent.parent.parent

ENV = BASE_DIR.joinpath(".env")

dotenv.load_dotenv(ENV)
PRODUCTION = os.getenv("PRODUCTION", "True").lower() in ["true", "1"]


def determine_data_dir() -> Path:
    global CWD
    global PRODUCTION
    global BASE_DIR
    if PRODUCTION:
        return Path("/app/data")

    return BASE_DIR.joinpath("dev", "data")
