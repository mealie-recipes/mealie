from settings import USE_MONGO, USE_TINYDB

from db.tinydb.tinydb_setup import TinyDatabase

tiny_db: TinyDatabase = None
if USE_TINYDB:

    tiny_db = TinyDatabase()

elif USE_MONGO:
    from db.mongo.mongo_setup import global_init as mongo_global_init

    mongo_global_init()
