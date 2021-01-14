from settings import DATA_DIR, USE_MONGO, USE_SQL

from db.sql.db_session import globa_init as sql_global_init
from db.tinydb.tinydb_setup import TinyDatabase

tiny_db: TinyDatabase = None
if USE_SQL:
    db_file = DATA_DIR.joinpath("mealie.sqlite")
    sql_global_init(db_file)

elif USE_MONGO:
    from db.mongo.mongo_setup import global_init as mongo_global_init

    mongo_global_init()
