import json

import requests
from fastapi.testclient import TestClient
from mealie.app import app
from mealie.core.config import app_dirs, settings
from mealie.db.db_setup import generate_session, sql_global_init
from pytest import fixture
from alembic import command, config
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests.app_routes import AppRoutes
from tests.test_config import TEST_DATA
from tests.utils.recipe_data import build_recipe_store, get_raw_no_image, get_raw_recipe

# sqlite test db
SQLITE_FILE = app_dirs.DATA_DIR.joinpath("test.db")
SQLITE_FILE.unlink(missing_ok=True)
DB_URL = "sqlite:///" + str(SQLITE_FILE.absolute())
engine = create_engine(
    DB_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

# alembic migrations
config = config.Config("alembic.ini")
config.set_main_option('sqlalchemy.url', DB_URL)
config.attributes['connection'] = engine
command.upgrade(config, "head")

# test session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


@fixture(scope="session")
def api_client():

    app.dependency_overrides[generate_session] = override_get_db

    yield TestClient(app)


@fixture(scope="session")
def api_routes():
    return AppRoutes()


@fixture(scope="session")
def test_image():
    return TEST_DATA.joinpath("test_image.jpg")


@fixture(scope="session")
def token(api_client: requests, api_routes: AppRoutes):
    form_data = {"username": "changeme@email.com", "password": settings.DEFAULT_PASSWORD}
    response = api_client.post(api_routes.auth_token, form_data)

    token = json.loads(response.text).get("access_token")

    return {"Authorization": f"Bearer {token}"}


@fixture(scope="session")
def raw_recipe():
    return get_raw_recipe()


@fixture(scope="session")
def raw_recipe_no_image():
    return get_raw_no_image()


@fixture(scope="session")
def recipe_store():
    return build_recipe_store()
