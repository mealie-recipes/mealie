import sqlalchemy as sa
from mealie.db.models.model_base import SqlAlchemyBase
from sqlalchemy.orm import sessionmaker


def sql_global_init(db_url: str):
    connect_args = {}
    if "sqlite" in db_url:
        connect_args["check_same_thread"] = False

    engine = sa.create_engine(db_url, echo=False, connect_args=connect_args)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    import mealie.db.models._all_models  # noqa: F401

    SqlAlchemyBase.metadata.create_all(engine)

    return SessionLocal
