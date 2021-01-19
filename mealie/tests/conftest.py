from app import app
from app_config import SQLITE_DIR
from db.db_setup import generate_session, sql_global_init
from fastapi.testclient import TestClient
from pytest import fixture

SQLITE_FILE = SQLITE_DIR.joinpath("test.db")
SQLITE_FILE.unlink(missing_ok=True)


TestSessionLocal = sql_global_init(SQLITE_FILE, check_thread=False)


def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


@fixture
def api_client():
    app.dependency_overrides[generate_session] = override_get_db
    return TestClient(app)
