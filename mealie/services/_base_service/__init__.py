from mealie.core.config import get_app_dirs, get_app_settings


class BaseService:
    def __init__(self) -> None:
        self.app_dirs = get_app_dirs()
        self.settings = get_app_settings()
