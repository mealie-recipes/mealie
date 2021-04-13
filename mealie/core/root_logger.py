import logging
import sys

from mealie.core.config import DATA_DIR

LOGGER_FILE = DATA_DIR.joinpath("mealie.log")
LOGGER_FORMAT = "%(levelname)s: \t%(message)s"
DATE_FORMAT = "%d-%b-%y %H:%M:%S"

logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT, datefmt="%d-%b-%y %H:%M:%S")


def logger_init() -> logging.Logger:
    """ Returns the Root Loggin Object for Mealie """
    logger = logging.getLogger("mealie")
    logger.propagate = False

    # File Handler
    output_file_handler = logging.FileHandler(LOGGER_FILE)
    handler_format = logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT)
    output_file_handler.setFormatter(handler_format)

    # Stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(handler_format)

    logger.addHandler(output_file_handler)
    logger.addHandler(stdout_handler)

    return logger


def get_logger(module=None) -> logging.Logger:
    """ Returns a child logger for mealie """
    global root_logger

    if module is None:
        return root_logger

    return root_logger.getChild(module)


root_logger = logger_init()
