from pathlib import Path

from app import app
from app_config import SQLITE_DIR
from db.db_setup import generate_session, sql_global_init
from fastapi.testclient import TestClient
from pytest import fixture
from services.settings_services import default_settings_init
from services.theme_services import default_theme_init

from tests.test_config import TEST_DATA

SQLITE_FILE = SQLITE_DIR.joinpath("test.db")
SQLITE_FILE.unlink(missing_ok=True)


TestSessionLocal = sql_global_init(SQLITE_FILE, check_thread=False)


def override_get_db():
    try:
        db = TestSessionLocal()
        default_theme_init()
        default_settings_init()
        yield db
    finally:
        db.close()


@fixture(scope="session")
def api_client():

    app.dependency_overrides[generate_session] = override_get_db
    yield TestClient(app)

    SQLITE_FILE.unlink()


@fixture(scope="session")
def test_image():
    return TEST_DATA.joinpath("test_image.jpg")
