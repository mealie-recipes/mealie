import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from mealie.core.config import get_settings

settings = get_settings()


def sql_global_init(db_url: str):
    connect_args = {}
    if "sqlite" in db_url:
        connect_args["check_same_thread"] = False

    engine = sa.create_engine(db_url, echo=False, connect_args=connect_args, pool_pre_ping=True)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return SessionLocal, engine


SessionLocal, engine = sql_global_init(settings.DB_URL)


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
