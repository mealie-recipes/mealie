from pathlib import Path

from services.settings_services import Colors, SiteTheme
from utils.logger import logger

CWD = Path(__file__).parent
DATA_DIR = CWD.joinpath("data")
TEMP_DIR = CWD.joinpath("data", "temp")


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.joinpath("img").mkdir(parents=True, exist_ok=True)
    DATA_DIR.joinpath("backups").mkdir(parents=True, exist_ok=True)
    DATA_DIR.joinpath("templates").mkdir(parents=True, exist_ok=True)
    DATA_DIR.joinpath("debug").mkdir(parents=True, exist_ok=True)


def generate_default_theme():
    default_colors = {
        "primary": "#E58325",
        "accent": "#00457A",
        "secondary": "#973542",
        "success": "#5AB1BB",
        "info": "#4990BA",
        "warning": "#FF4081",
        "error": "#EF5350",
    }

    try:
        SiteTheme.get_by_name("default")
        return "default theme exists"
    except:
        logger.info("Generating Default Theme")
        colors = Colors(**default_colors)
        default_theme = SiteTheme(name="default", colors=colors)
        default_theme.save_to_db()


if __name__ == "__main__":
    pass
