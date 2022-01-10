from pathlib import Path

CWD = Path(__file__).parent
PROJECT_DIR = Path(__file__).parent.parent.parent


class Directories:
    out_dir = CWD / "generated"


class CodeTemplates:
    interface = CWD / "templates" / "interface.js"
    pytest_routes = CWD / "templates" / "test_routes.py.j2"


class CodeDest:
    interface = CWD / "generated" / "interface.js"
    pytest_routes = CWD / "generated" / "test_routes.py"


class CodeKeys:
    """Hard coded comment IDs that are used to generate code"""

    nuxt_local_messages = "MESSAGE_LOCALES"
    nuxt_local_dates = "DATE_LOCALES"
