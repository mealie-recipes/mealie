from mealie.core.config import get_app_dirs, get_settings
from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session

logger = get_logger()


class BaseService:
    def __init__(self) -> None:
        # Static Globals Dependency Injection
        self.db = get_database()
        self.app_dirs = get_app_dirs()
        self.settings = get_settings()

    def session_context(self):
        return generate_session()
