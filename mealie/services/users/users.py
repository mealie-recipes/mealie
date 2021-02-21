from db.database import db
from db.db_setup import create_session, sql_exists
from fastapi.logger import logger


def init_super_user():
    session = create_session()

    default_user = {
        "full_name": "Change Me",
        "email": "changeme@email.com",
        "password": "MyPassword",
        "family": "public",
        "is_superuser": True,
    }

    logger.info("Generating Default User")

    db.users.create(session, default_user)

    session.close()


if not sql_exists:
    init_super_user()
