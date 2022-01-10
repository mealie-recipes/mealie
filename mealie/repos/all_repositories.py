from fastapi import Depends
from sqlalchemy.orm import Session

from mealie.db.db_setup import generate_session

from .repository_factory import AllRepositories


def generate_repositories(session: Session = Depends(generate_session)):
    return AllRepositories(session)


def get_repositories(session: Session):
    return AllRepositories(session)
