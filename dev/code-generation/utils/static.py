from pathlib import Path

PARENT = Path(__file__).parent.parent
PROJECT_DIR = Path(__file__).parent.parent.parent.parent


class Directories:
    out_dir = PARENT / "generated"


class CodeTemplates:
    interface = PARENT / "templates" / "interface.js"
    pytest_routes = PARENT / "templates" / "test_routes.py.j2"


class CodeDest:
    interface = PARENT / "generated" / "interface.js"
    pytest_routes = PARENT / "generated" / "test_routes.py"
    use_locales = PROJECT_DIR / "frontend" / "composables" / "use-locales" / "available-locales.ts"


class CodeKeys:
    """Hard coded comment IDs that are used to generate code"""

    nuxt_local_messages = "MESSAGE_LOCALES"
    nuxt_local_dates = "DATE_LOCALES"
