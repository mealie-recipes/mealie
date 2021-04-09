from enum import Enum
from pathlib import Path

from fastapi.logger import logger
from mealie.schema.migration import MigrationImport
from mealie.services.migrations import chowdown, chowdown, nextcloud
from sqlalchemy.orm.session import Session


class Migration(str, Enum):
    """The class defining the supported types of migrations for Mealie. Pass the
    class attribute of the class instead of the string when using.
    """

    nextcloud = "nextcloud"
    chowdown = "chowdown"


def migrate(migration_type: str, file_path: Path, session: Session) -> list[MigrationImport]:
    """The new entry point for accessing migrations within the 'migrations' service.
    Using the 'Migrations' enum class as a selector for migration_type to direct which function
    to call. All migrations will return a MigrationImport object that is built for displaying
    detailed information on the frontend. This will provide a single point of access

    Args:
        migration_type (str): a string option representing the migration type. See Migration attributes for options
        file_path (Path): Path to the zip file containing the data
        session (Session): a SqlAlchemy Session

    Returns:
        list[MigrationImport]: [description]
    """

    logger.info(f"Starting Migration from {migration_type}")

    if migration_type == Migration.nextcloud.value:
        migration_imports = nextcloud.migrate(session, file_path)

    elif migration_type == Migration.chowdown.value:
        migration_imports = chowdown.migrate(session, file_path)

    else:
        return []

    logger.info(f"Finishing Migration from {migration_type}")

    return migration_imports
