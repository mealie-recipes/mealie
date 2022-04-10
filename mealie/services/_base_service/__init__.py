from mealie.core.config import get_app_dirs, get_app_settings
from mealie.core.root_logger import get_logger


class BaseService:
    def __init__(self) -> None:
        self.directories = get_app_dirs()
        self.settings = get_app_settings()
        self.logger = get_logger()
