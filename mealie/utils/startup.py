from pathlib import Path

from app_config import REQUIRED_DIRS
from services.settings_services import default_theme_init

CWD = Path(__file__).parent


def pre_start():
    ensure_dirs()
    default_theme_init()


def ensure_dirs():
    for dir in REQUIRED_DIRS:
        dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    pass
