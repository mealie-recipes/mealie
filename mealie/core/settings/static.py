import os
from pathlib import Path

APP_VERSION = "v1.0.0b"
DB_VERSION = "v1.0.0b"

CWD = Path(__file__).parent
BASE_DIR = CWD.parent.parent.parent

PRODUCTION = os.getenv("PRODUCTION", "True").lower() in ["true", "1"]
