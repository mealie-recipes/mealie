import datetime

from sqlalchemy import delete

from mealie.core import root_logger
from mealie.db.db_setup import session_context
from mealie.db.models.users.password_reset import PasswordResetModel

logger = root_logger.get_logger()

MAX_DAYS_OLD = 2


def purge_password_reset_tokens():
    """Purges all events after x days"""
    logger.debug("purging password reset tokens")
    limit = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=MAX_DAYS_OLD)

    with session_context() as session:
        stmt = delete(PasswordResetModel).filter(PasswordResetModel.created_at <= limit)
        session.execute(stmt)
        session.commit()
        session.close()
        logger.info("password reset tokens purged")
