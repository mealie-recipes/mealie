from app_config import SQLITE_FILE, USE_MONGO, USE_SQL

from db.sql.db_session import globa_init as sql_global_init

sql_exists = SQLITE_FILE.is_file()

if USE_SQL:
    sql_global_init(SQLITE_FILE)

    pass

elif USE_MONGO:
    from db.mongo.mongo_setup import global_init as mongo_global_init

    mongo_global_init()
