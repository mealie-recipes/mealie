from mealie.core import root_logger
from mealie.core.config import get_app_dirs

app_dirs = get_app_dirs()
from mealie.db.db_setup import create_session
from mealie.services.backups.exports import backup_all
from mealie.services.events import create_backup_event

logger = root_logger.get_logger()


def auto_backup():
    for backup in app_dirs.BACKUP_DIR.glob("Auto*.zip"):
        backup.unlink()

    templates = [template for template in app_dirs.TEMPLATE_DIR.iterdir()]
    session = create_session()
    backup_all(session=session, tag="Auto", templates=templates)
    logger.info("generating automated backup")
    create_backup_event("Automated Backup", "Automated backup created", session)
    session.close()
    logger.info("automated backup generated")
