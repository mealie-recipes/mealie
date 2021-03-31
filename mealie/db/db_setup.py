from mealie.core.config import settings
from sqlalchemy.orm.session import Session

from mealie.db.models.db_session import sql_global_init

sql_exists = True

sql_exists = settings.SQLITE_FILE.is_file()
SessionLocal = sql_global_init(settings.SQLITE_FILE)


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
