from mealie.core.config import settings
from sqlalchemy.orm.session import Session

from mealie.db.models.db_session import sql_global_init

sql_exists = True

SessionLocal = sql_global_init(settings.DB_URL)


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
