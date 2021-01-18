import mongoengine
from app_config import DB_HOST, DB_PASSWORD, DB_PORT, DB_USERNAME, MEALIE_DB_NAME
from utils.logger import logger


def global_init():
    mongoengine.register_connection(
        alias="core",
        name=MEALIE_DB_NAME,
        host=DB_HOST,
        port=int(DB_PORT),
        username=DB_USERNAME,
        password=DB_PASSWORD,
        authentication_source="admin",
    )

    logger.info("Mongo Data Initialized")
