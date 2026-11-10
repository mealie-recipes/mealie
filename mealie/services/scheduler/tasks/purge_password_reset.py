import datetime

from sqlalchemy import delete

from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.db.db_setup import session_context
from mealie.db.models.users.password_reset import PasswordResetModel

logger = root_logger.get_logger()


def purge_password_reset_tokens():
    """Purges tokens older than the password reset token lifetime"""
    logger.debug("purging password reset tokens")
    limit = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=get_app_settings().PASSWORD_RESET_TOKEN_TIME)

    with session_context() as session:
        stmt = delete(PasswordResetModel).filter(PasswordResetModel.created_at <= limit)
        session.execute(stmt)
        session.commit()
        session.close()
        logger.info("password reset tokens purged")
