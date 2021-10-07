import datetime

from mealie.core import root_logger
from mealie.db.db_setup import create_session
from mealie.db.models.group import GroupInviteToken

logger = root_logger.get_logger()

MAX_DAYS_OLD = 4


def purge_group_registration():
    """Purges all events after x days"""
    logger.info("purging expired registration tokens")
    limit = datetime.datetime.now() - datetime.timedelta(days=MAX_DAYS_OLD)
    session = create_session()
    session.query(GroupInviteToken).filter(GroupInviteToken.created_at <= limit).delete()
    session.commit()
    session.close()
    logger.info("registration token purged")
