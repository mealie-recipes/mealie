import logging
import sys
from dataclasses import dataclass
from functools import lru_cache

from mealie.core.config import determine_data_dir

DATA_DIR = determine_data_dir()

from .config import get_app_settings

LOGGER_FILE = DATA_DIR.joinpath("mealie.log")
DATE_FORMAT = "%d-%b-%y %H:%M:%S"
LOGGER_FORMAT = "%(levelname)s: %(asctime)s \t%(message)s"


@dataclass
class LoggerConfig:
    handlers: list
    format: str
    date_format: str
    logger_file: str
    level: int = logging.INFO


@lru_cache
def get_logger_config():
    settings = get_app_settings()

    if not settings.PRODUCTION:
        from rich.logging import RichHandler

        return LoggerConfig(
            handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
            format=None,
            date_format=None,
            logger_file=None,
        )

    output_file_handler = logging.FileHandler(LOGGER_FILE)
    handler_format = logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT)
    output_file_handler.setFormatter(handler_format)

    # Stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(handler_format)

    return LoggerConfig(
        handlers=[output_file_handler, stdout_handler],
        format="%(levelname)s: %(asctime)s \t%(message)s",
        date_format="%d-%b-%y %H:%M:%S",
        logger_file=LOGGER_FILE,
    )


logger_config = get_logger_config()

logging.basicConfig(
    level=logger_config.level,
    format=logger_config.format,
    datefmt=logger_config.date_format,
    handlers=logger_config.handlers,
)


def logger_init() -> logging.Logger:
    """Returns the Root Loggin Object for Mealie"""
    return logging.getLogger("mealie")


root_logger = logger_init()


def get_logger(module=None) -> logging.Logger:
    """Returns a child logger for mealie"""
    global root_logger

    if module is None:
        return root_logger

    return root_logger.getChild(module)
