import mongoengine
from settings import DB_HOST, DB_PASSWORD, DB_PORT, DB_USERNAME, MEALIE_DB_NAME


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
