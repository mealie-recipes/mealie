import datetime

from mealie.core import root_logger
from mealie.db.db_setup import create_session
from mealie.db.models.users.password_reset import PasswordResetModel

logger = root_logger.get_logger()

MAX_DAYS_OLD = 2


def purge_password_reset_tokens():
    """Purges all events after x days"""
    logger.info("purging password reset tokens")
    limit = datetime.datetime.now() - datetime.timedelta(days=MAX_DAYS_OLD)
    session = create_session()
    session.query(PasswordResetModel).filter(PasswordResetModel.created_at <= limit).delete()
    session.commit()
    session.close()
    logger.info("password reset tokens purges")
