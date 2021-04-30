from mealie.core.config import settings
from mealie.db.models.db_session import sql_global_init
from sqlalchemy.orm.session import Session

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
