from tests.pre_test import settings  # isort:skip

from fastapi.testclient import TestClient
from pytest import fixture

from mealie.app import app
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
        settings.DB_PROVIDER.db_path.unlink()  # Handle SQLite Provider
    except Exception:
        pass


@fixture(scope="session")
def test_image_jpg():
    return test_data.images_test_image_1


@fixture(scope="session")
def test_image_png():
    return test_data.images_test_image_2
