from getpass import getpass

from mealie.core import root_logger
from mealie.core.security.security import hash_password
from mealie.db.db_setup import session_context
from mealie.repos.repository_factory import AllRepositories


def main():
    confirmed = input("Please enter the email of the user you want to reset: ")

    logger = root_logger.get_logger()

    with session_context() as session:
        repos = AllRepositories(session)

        user = repos.users.get_one(confirmed, "email")

        if not user:
            logger.error("no user found")
            exit(1)

        logger.info(f"changing password for {user.username}")

        pw = getpass("Please enter the new password: ")
        pw2 = getpass("Please enter the new password again: ")

        if pw != pw2:
            logger.error("passwords do not match")

        hashed_password = hash_password(pw)
        repos.users.update_password(user.id, hashed_password)

    logger.info("password change successful")
    input("press enter to exit ")
    exit(0)


if __name__ == "__main__":
    main()
