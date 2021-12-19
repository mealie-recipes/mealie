import pytest

from mealie.db.database import Database, get_database
from mealie.db.db_setup import SessionLocal


@pytest.fixture()
def database() -> Database:
    try:
        db = SessionLocal()
        yield get_database(db)

    finally:
        db.close()
