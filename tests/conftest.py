from tests.pre_test import settings  # isort:skip

from fastapi.testclient import TestClient
from pytest import fixture

from mealie.app import app
from mealie.db.db_setup import SessionLocal, generate_session
from mealie.db.init_db import main
from tests.fixtures import *  # noqa: F403 F401
from tests.test_config import TEST_DATA

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
        settings.DB_PROVIDER.db_path.unlink()  # Handle SQLite Provider
    except Exception:
        pass


@fixture(scope="session")
def test_image_jpg():
    return TEST_DATA.joinpath("images", "test_image.jpg")


@fixture(scope="session")
def test_image_png():
    return TEST_DATA.joinpath("images", "test_image.png")
