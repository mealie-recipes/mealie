import sys
from getpass import getpass

from mealie.core import root_logger
from mealie.core.security.security import hash_password
from mealie.db.db_setup import session_context
from mealie.db.models.users.users import AuthMethod
from mealie.repos.repository_factory import AllRepositories


def main():
    confirmed = input("Please enter the email of the user you want to reset: ")

    logger = root_logger.get_logger()

    with session_context() as session:
        repos = AllRepositories(session, group_id=None, household_id=None)

        user = repos.users.get_one(confirmed, "email")

        if not user:
            logger.error("no user found")
            sys.exit(1)

        reset_auth_method = False
        if user.auth_method != AuthMethod.MEALIE:
            logger.warning("%s is using external authentication.", user.username)
            response = input("Would you like to change your authentication method back to local? (y/n): ")
            reset_auth_method = response.lower() == "yes" or response.lower() == "y"

        logger.info("changing password for %s", user.username)

        pw = getpass("Please enter the new password: ")
        pw2 = getpass("Please enter the new password again: ")

        if pw != pw2:
            logger.error("passwords do not match")
            sys.exit(1)

        hashed_password = hash_password(pw)
        repos.users.update_password(user.id, hashed_password)
        if reset_auth_method:
            user.auth_method = AuthMethod.MEALIE
            repos.users.update(user.id, user)

    logger.info("password change successful")
    input("press enter to exit ")
    sys.exit(0)


if __name__ == "__main__":
    main()
