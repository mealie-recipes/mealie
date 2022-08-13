from mealie.core import root_logger
from mealie.db.db_setup import with_session
from mealie.repos.repository_factory import AllRepositories
from mealie.services.user_services.user_service import UserService


def locked_user_reset():
    logger = root_logger.get_logger()
    logger.info("resetting locked users")

    with with_session() as session:
        repos = AllRepositories(session)
        user_service = UserService(repos)

        unlocked = user_service.reset_locked_users()
        logger.info(f"scheduled task unlocked {unlocked} users in the database")
        logger.info("locked users reset")
