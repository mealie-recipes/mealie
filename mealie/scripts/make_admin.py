import sys

from mealie.core import root_logger
from mealie.db.db_setup import session_context
from mealie.repos.repository_factory import AllRepositories


def main():
    confirmed = input("Enter user email to assign this user admin privileges: ")

    logger = root_logger.get_logger()

    with session_context() as session:
        repos = AllRepositories(session, group_id=None, household_id=None)

        user = repos.users.get_one(confirmed, "email")
        if not user:
            logger.error("no user found")
            sys.exit(1)

        user.admin = True
        repos.users.update(user.id, user)

    logger.info("updated user %s to admin", user.username)
    input("press enter to exit ")
    sys.exit(0)


if __name__ == "__main__":
    main()
