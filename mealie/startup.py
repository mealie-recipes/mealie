import json
from pathlib import Path

from db.mongo_setup import global_init as mongo_global_init
from db.sql.db_session import global_init as sql_global_init
from services.scheduler_services import Scheduler
from services.settings_services import Colors, SiteTheme
from settings import DATA_DIR, MONGO, SQLITE
from utils.logger import logger

CWD = Path(__file__).parent

scheduler = None


def pre_start():
    if SQLITE:
        from settings import SQLITE_DB_FILE

        sql_global_init(SQLITE_DB_FILE)
    elif MONGO:
        mongo_global_init()

    global scheduler
    scheduler = Scheduler()
    scheduler.startup_scheduler()

    ensure_dirs()
    generate_default_theme()


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


"""Script to export the ReDoc documentation page into a standalone HTML file."""

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>My Project - ReDoc</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <style>
        body {
            margin: 0;
            padding: 0;
        }
    </style>
    <style data-styled="" data-styled-version="4.4.1"></style>
</head>
<body>
    <div id="redoc-container"></div>
    <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"> </script>
    <script>
        var spec = %s;
        Redoc.init(spec, {}, document.getElementById("redoc-container"));
    </script>
</body>
</html>
"""

out_path = CWD.joinpath("temp", "index.html")


def generate_api_docs(app):
    with open(out_path, "w") as fd:
        out_path.parent.mkdir(exist_ok=True)
        print(HTML_TEMPLATE % json.dumps(app.openapi()), file=fd)


if __name__ == "__main__":
    pass
