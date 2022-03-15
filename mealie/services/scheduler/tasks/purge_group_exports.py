import datetime
from pathlib import Path

from mealie.core import root_logger
from mealie.core.config import get_app_dirs
from mealie.db.db_setup import create_session
from mealie.db.models.group.exports import GroupDataExportsModel

ONE_DAY_AS_MINUTES = 1440


def purge_group_data_exports(max_minutes_old=ONE_DAY_AS_MINUTES):
    """Purges all group exports after x days"""
    logger = root_logger.get_logger()

    logger.info("purging group data exports")
    limit = datetime.datetime.now() - datetime.timedelta(minutes=max_minutes_old)
    session = create_session()

    results = session.query(GroupDataExportsModel).filter(GroupDataExportsModel.expires <= limit)

    total_removed = 0
    for result in results:
        session.delete(result)
        Path(result.path).unlink(missing_ok=True)
        total_removed += 1

    session.commit()
    session.close()

    logger.info(f"finished purging group data exports. {total_removed} exports removed from group data")


def purge_excess_files() -> None:
    """Purges all files in the uploads directory that are older than 2 days"""
    directories = get_app_dirs()
    logger = root_logger.get_logger()

    limit = datetime.datetime.now() - datetime.timedelta(minutes=ONE_DAY_AS_MINUTES * 2)

    for file in directories.GROUPS_DIR.glob("**/export/*.zip"):
        # TODO: fix comparison types
        if file.stat().st_mtime < limit:  # type: ignore
            file.unlink()
            logger.info(f"excess group file removed '{file}'")

    logger.info("finished purging excess files")
