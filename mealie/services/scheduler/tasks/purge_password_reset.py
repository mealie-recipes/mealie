from mealie.core import root_logger

logger = root_logger.get_logger()

MAX_DAYS_OLD = 4


def purge_password_reset_tokens():
    """Purges all events after x days"""
    logger.info("purging password reset tokens")
    logger.info("password reset tokens purges")
