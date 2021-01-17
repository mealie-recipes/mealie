from app_config import SQLITE_DIR, USE_MONGO, USE_SQL

from db.sql.db_session import globa_init as sql_global_init

if USE_SQL:
    db_file = SQLITE_DIR.joinpath("mealie.sqlite")
    sql_global_init(db_file)

elif USE_MONGO:
    from db.mongo.mongo_setup import global_init as mongo_global_init

    mongo_global_init()
