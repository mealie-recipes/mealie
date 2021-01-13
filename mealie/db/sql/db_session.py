from pathlib import Path

import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import SqlAlchemyBase

factory = None


def globa_init(db_file: Path):
    global factory

    if factory:
        return

    conn_str = "sqlite:///" + db_file.absolute()

    engine = sa.create_engine(conn_str, echo=False)

    factory = orm.sessionmaker(bind=engine)

    import db.sql._all_models

    SqlAlchemyBase.metadata.create_all(engine)
