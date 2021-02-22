from core.config import SQLITE_FILE, USE_SQL
from sqlalchemy.orm.session import Session

from db.models.db_session import sql_global_init

sql_exists = True

if USE_SQL:
    sql_exists = SQLITE_FILE.is_file()
    SessionLocal = sql_global_init(SQLITE_FILE)
else:
    raise Exception("Cannot identify database type")


def create_session() -> Session:
    global SessionLocal
    return SessionLocal()


def generate_session() -> Session:
    global SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
