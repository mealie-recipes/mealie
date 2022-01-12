from mealie.core.config import get_app_dirs, get_app_settings
from mealie.core.root_logger import get_logger
from mealie.lang import get_locale_provider


class BaseService:
    def __init__(self) -> None:
        self.directories = get_app_dirs()
        self.settings = get_app_settings()
        self.t = get_locale_provider()
        self.logger = get_logger()
