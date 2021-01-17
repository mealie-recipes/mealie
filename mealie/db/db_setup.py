from app_config import SQLITE_FILE, USE_SQL

from db.sql.db_session import globa_init as sql_global_init

sql_exists = SQLITE_FILE.is_file()

if USE_SQL:
    sql_global_init(SQLITE_FILE)

    pass

else:
    raise Exception("Cannot identify database type")
