from pathlib import Path

from app_config import REQUIRED_DIRS
from services.settings_services import default_theme_init

CWD = Path(__file__).parent


def post_start():
    default_theme_init()





if __name__ == "__main__":
    pass
