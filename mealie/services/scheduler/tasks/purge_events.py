import datetime

from mealie.core import root_logger
from mealie.db.db_setup import create_session
from mealie.db.models.event import Event

logger = root_logger.get_logger()


def purge_events_database():
    """Purges all events after 100"""
    logger.info("Purging Events in Database")
    expiration_days = 7
    limit = datetime.datetime.now() - datetime.timedelta(days=expiration_days)
    session = create_session()
    session.query(Event).filter(Event.time_stamp <= limit).delete()
    session.commit()
    session.close()
    logger.info("Events Purges")
