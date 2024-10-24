from mealie.core import root_logger
from mealie.db.db_setup import session_context
from mealie.repos.repository_factory import AllRepositories
from mealie.services.user_services.user_service import UserService


def locked_user_reset():
    logger = root_logger.get_logger()
    logger.debug("resetting locked users")

    with session_context() as session:
        repos = AllRepositories(session, group_id=None, household_id=None)
        user_service = UserService(repos)

        unlocked = user_service.reset_locked_users()
        logger.debug(f"scheduled task unlocked {unlocked} users in the database")
        logger.info("locked users reset")
        return unlocked
