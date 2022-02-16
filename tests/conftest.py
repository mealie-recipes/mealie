from pytest import MonkeyPatch, fixture

mp = MonkeyPatch()
mp.setenv("PRODUCTION", "True")
mp.setenv("TESTING", "True")


from pathlib import Path

from fastapi.testclient import TestClient

from mealie.app import app
from mealie.core import config
from mealie.db.db_setup import SessionLocal, generate_session
from mealie.db.init_db import main
from tests import data as test_data
from tests.fixtures import *  # noqa: F403 F401

main()


def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@fixture(scope="session")
def api_client():

    app.dependency_overrides[generate_session] = override_get_db

    yield TestClient(app)

    try:
        settings = config.get_app_settings()
        settings.DB_PROVIDER.db_path.unlink()  # Handle SQLite Provider
    except Exception:
        pass


@fixture(scope="session")
def test_image_jpg():
    return test_data.images_test_image_1


@fixture(scope="session")
def test_image_png():
    return test_data.images_test_image_2


@fixture(scope="session", autouse=True)
def global_cleanup() -> None:
    """Purges the .temp directory used for testing"""
    yield None
    try:
        temp_dir = Path(__file__).parent / ".temp"

        if temp_dir.exists():
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception:
        pass
