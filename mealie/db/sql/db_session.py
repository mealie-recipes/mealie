from pathlib import Path

import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import SqlAlchemyBase
from sqlalchemy.orm.session import Session

__factory = None


def globa_init(db_file: Path):
    global __factory

    if __factory:
        return
    conn_str = "sqlite:///" + str(db_file.absolute())

    engine = sa.create_engine(
        conn_str, echo=False, connect_args={"check_same_thread": False}
    )

    __factory = orm.sessionmaker(bind=engine)

    import db.sql._all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
