from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security import hash_password
from mealie.repos.repository_factory import AllRepositories

logger = root_logger.get_logger("init_users")
settings = get_app_settings()


def dev_users() -> list[dict]:
    return [
        {
            "full_name": "Jason",
            "username": "jason",
            "email": "jason@example.com",
            "password": hash_password(settings._DEFAULT_PASSWORD),
            "group": settings.DEFAULT_GROUP,
            "household": settings.DEFAULT_HOUSEHOLD,
            "admin": False,
        },
        {
            "full_name": "Bob",
            "username": "bob",
            "email": "bob@example.com",
            "password": hash_password(settings._DEFAULT_PASSWORD),
            "group": settings.DEFAULT_GROUP,
            "household": settings.DEFAULT_HOUSEHOLD,
            "admin": False,
        },
        {
            "full_name": "Sarah",
            "username": "sarah",
            "email": "sarah@example.com",
            "password": hash_password(settings._DEFAULT_PASSWORD),
            "group": settings.DEFAULT_GROUP,
            "household": settings.DEFAULT_HOUSEHOLD,
            "admin": False,
        },
        {
            "full_name": "Sammy",
            "username": "sammy",
            "email": "sammy@example.com",
            "password": hash_password(settings._DEFAULT_PASSWORD),
            "group": settings.DEFAULT_GROUP,
            "household": settings.DEFAULT_HOUSEHOLD,
            "admin": False,
        },
    ]


def default_user_init(db: AllRepositories):
    default_user = {
        "full_name": "Change Me",
        "username": "admin",
        "email": settings._DEFAULT_EMAIL,
        "password": hash_password(settings._DEFAULT_PASSWORD),
        "group": settings.DEFAULT_GROUP,
        "household": settings.DEFAULT_HOUSEHOLD,
        "admin": True,
    }

    logger.info("Generating Default User")
    db.users.create(default_user)

    if not settings.PRODUCTION:
        for user in dev_users():
            db.users.create(user)
