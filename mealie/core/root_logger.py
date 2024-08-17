import logging

from .config import get_app_dirs, get_logging_settings
from .logger.config import configured_logger

__root_logger: None | logging.Logger = None


def get_logger(module=None) -> logging.Logger:
    """
    Get a logger instance for a module, in most cases module should not be
    provided. Simply using the root logger is sufficient.

    Cases where you would want to use a module specific logger might be a background
    task or a long running process where you want to easily identify the source of
    those messages
    """
    global __root_logger

    if __root_logger is None:
        app_logging_settings = get_logging_settings()

        mode = "development"

        if app_logging_settings.TESTING:
            mode = "testing"
        elif app_logging_settings.PRODUCTION:
            mode = "production"

        dirs = get_app_dirs()

        substitutions = {
            "DATA_DIR": dirs.DATA_DIR.as_posix(),
            "LOG_LEVEL": app_logging_settings.LOG_LEVEL.upper(),
        }

        __root_logger = configured_logger(
            mode=mode,
            config_override=app_logging_settings.LOG_CONFIG_OVERRIDE,
            substitutions=substitutions,
        )

    if module is None:
        return __root_logger

    return __root_logger.getChild(module)
