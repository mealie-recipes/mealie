from mealie.core import root_logger
from mealie.core.config import get_app_settings
from mealie.core.security import hash_password
from mealie.db.data_access_layer.access_model_factory import Database

logger = root_logger.get_logger("init_users")
settings = get_app_settings()


def dev_users() -> list[dict]:
    return [
        {
            "full_name": "Jason",
            "username": "jason",
            "email": "jason@email.com",
            "password": hash_password(settings.DEFAULT_PASSWORD),
            "group": settings.DEFAULT_GROUP,
            "admin": False,
        },
        {
            "full_name": "Bob",
            "username": "bob",
            "email": "bob@email.com",
            "password": hash_password(settings.DEFAULT_PASSWORD),
            "group": settings.DEFAULT_GROUP,
            "admin": False,
        },
        {
            "full_name": "Sarah",
            "username": "sarah",
            "email": "sarah@email.com",
            "password": hash_password(settings.DEFAULT_PASSWORD),
            "group": settings.DEFAULT_GROUP,
            "admin": False,
        },
        {
            "full_name": "Sammy",
            "username": "sammy",
            "email": "sammy@email.com",
            "password": hash_password(settings.DEFAULT_PASSWORD),
            "group": settings.DEFAULT_GROUP,
            "admin": False,
        },
    ]


def default_user_init(db: Database):
    default_user = {
        "full_name": "Change Me",
        "username": "admin",
        "email": settings.DEFAULT_EMAIL,
        "password": hash_password(settings.DEFAULT_PASSWORD),
        "group": settings.DEFAULT_GROUP,
        "admin": True,
    }

    logger.info("Generating Default User")
    db.users.create(default_user)

    if not settings.PRODUCTION:
        for user in dev_users():
            db.users.create(user)
