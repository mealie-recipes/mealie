import mongoengine
from settings import DB_HOST, DB_PASSWORD, DB_PORT, DB_USERNAME



def global_init():
    mongoengine.register_connection(
        alias="core",
        name="demo_mealie",
        host=DB_HOST,
        port=int(DB_PORT),
        username=DB_USERNAME,
        password=DB_PASSWORD,
        authentication_source="admin",
    )

