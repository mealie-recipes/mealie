from sqlalchemy.orm import Session

from .data_access_layer.access_model_factory import Database


def get_database(session: Session):
    return Database(session)
