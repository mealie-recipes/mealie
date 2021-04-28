import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


def sql_global_init(db_url: str):
    thread_safe = True
    if "sqlite" in db_url:
        thread_safe = False

    engine = sa.create_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": thread_safe},
    )

    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
