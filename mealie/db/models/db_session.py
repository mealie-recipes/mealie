from pathlib import Path

import sqlalchemy as sa
from db.models.model_base import SqlAlchemyBase
from sqlalchemy.orm import sessionmaker


def sql_global_init(db_file: Path, check_thread=False):

    SQLALCHEMY_DATABASE_URL = "sqlite:///" + str(db_file.absolute())
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

    engine = sa.create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": check_thread},
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    import db.models._all_models

    SqlAlchemyBase.metadata.create_all(engine)

    return SessionLocal
