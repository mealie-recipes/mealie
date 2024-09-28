from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session, sessionmaker

from mealie.db.db_setup import SessionLocal
from mealie.repos.all_repositories import AllRepositories, get_repositories


@pytest.fixture(scope="module")
def session() -> Generator[sessionmaker[Session], None, None]:
    try:
        sess = SessionLocal()
        yield sess
    finally:
        sess.close()


@pytest.fixture()
def unfiltered_database(session: Session) -> Generator[AllRepositories, None, None]:
    yield get_repositories(session, group_id=None, household_id=None)
