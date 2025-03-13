from fastapi.testclient import TestClient

from mealie.schema.response.pagination import PaginationQuery
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def test_seed_invalid_locale(api_client: TestClient, unique_user: TestUser):
    for route in (api_routes.groups_seeders_foods, api_routes.groups_seeders_labels, api_routes.groups_seeders_units):
        resp = api_client.post(route, json={"locale": "invalid"}, headers=unique_user.token)
        assert resp.status_code == 422


def test_seed_foods(api_client: TestClient, unique_user: TestUser):
    CREATED_FOODS = 214
    database = unique_user.repos

    # Check that the foods was created
    foods = database.ingredient_foods.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert len(foods) == 0

    resp = api_client.post(api_routes.groups_seeders_foods, json={"locale": "en-US"}, headers=unique_user.token)
    assert resp.status_code == 200

    # Check that the foods was created
    foods = database.ingredient_foods.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert len(foods) == CREATED_FOODS


def test_seed_units(api_client: TestClient, unique_user: TestUser):
    CREATED_UNITS = 23
    database = unique_user.repos

    # Check that the foods was created
    units = database.ingredient_units.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert len(units) == 0

    resp = api_client.post(api_routes.groups_seeders_units, json={"locale": "en-US"}, headers=unique_user.token)
    assert resp.status_code == 200

    # Check that the foods was created
    units = database.ingredient_units.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert len(units) == CREATED_UNITS


def test_seed_labels(api_client: TestClient, unique_user: TestUser):
    CREATED_LABELS = 21
    database = unique_user.repos

    # Check that the foods was created
    labels = database.group_multi_purpose_labels.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert len(labels) == 0

    resp = api_client.post(api_routes.groups_seeders_labels, json={"locale": "en-US"}, headers=unique_user.token)
    assert resp.status_code == 200

    # Check that the foods was created
    labels = database.group_multi_purpose_labels.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert len(labels) == CREATED_LABELS
