from pathlib import Path

import sqlalchemy as sa
import sqlalchemy.orm as orm
from settings import SQLITE


factory = None

def global_init(db_file: Path):
    if not SQLITE:
        pass

    global factory

    if factory:
        return

    if not db_file or not db_file.strip:
        raise Exception("You must Specif a db file")

    conn_str = "sqlite:///" + db_file.absolute()

    engine = sa.create_engine(conn_str, echo=False)

    factory = orm.sessionmaker(bind=engine)
