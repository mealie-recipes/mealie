from pathlib import Path

from app_config import REQUIRED_DIRS

CWD = Path(__file__).parent


def pre_start():
    ensure_dirs()


def ensure_dirs():
    for dir in REQUIRED_DIRS:
        dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    pass
