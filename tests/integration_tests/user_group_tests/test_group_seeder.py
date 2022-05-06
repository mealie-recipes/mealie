from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.utils import routes
from tests.utils.fixture_schemas import TestUser


def test_seed_invalid_locale(api_client: TestClient, unique_user: TestUser):
    for route in [routes.seeders.Seeders.foods, routes.seeders.Seeders.labels, routes.seeders.Seeders.units]:
        resp = api_client.post(route, json={"locale": "invalid"}, headers=unique_user.token)
        assert resp.status_code == 422


def test_seed_foods(api_client: TestClient, unique_user: TestUser, database: AllRepositories):
    CREATED_FOODS = 220

    # Check that the foods was created
    foods = database.ingredient_foods.by_group(unique_user.group_id).get_all()
    assert len(foods) == 0

    resp = api_client.post(routes.seeders.Seeders.foods, json={"locale": "en-US"}, headers=unique_user.token)
    assert resp.status_code == 200

    # Check that the foods was created
    foods = database.ingredient_foods.by_group(unique_user.group_id).get_all()
    assert len(foods) == CREATED_FOODS


def test_seed_units(api_client: TestClient, unique_user: TestUser, database: AllRepositories):
    CREATED_UNITS = 20

    # Check that the foods was created
    units = database.ingredient_units.by_group(unique_user.group_id).get_all()
    assert len(units) == 0

    resp = api_client.post(routes.seeders.Seeders.units, json={"locale": "en-US"}, headers=unique_user.token)
    assert resp.status_code == 200

    # Check that the foods was created
    units = database.ingredient_units.by_group(unique_user.group_id).get_all()
    assert len(units) == CREATED_UNITS


def test_seed_labels(api_client: TestClient, unique_user: TestUser, database: AllRepositories):
    CREATED_LABELS = 21

    # Check that the foods was created
    labels = database.group_multi_purpose_labels.by_group(unique_user.group_id).get_all()
    assert len(labels) == 0

    resp = api_client.post(routes.seeders.Seeders.labels, json={"locale": "en-US"}, headers=unique_user.token)
    assert resp.status_code == 200

    # Check that the foods was created
    labels = database.group_multi_purpose_labels.by_group(unique_user.group_id).get_all()
    assert len(labels) == CREATED_LABELS
