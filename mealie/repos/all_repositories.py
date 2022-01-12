from sqlalchemy.orm import Session

from .repository_factory import AllRepositories


def get_repositories(session: Session):
    return AllRepositories(session)
