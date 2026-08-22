from fastapi.testclient import TestClient

from mealie.schema.response.pagination import PaginationQuery
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser
from tests.utils.seed_data import seeded_food_names, seeded_label_names, seeded_unit_names

LOCALE = "en-US"


def test_seed_invalid_locale(api_client: TestClient, unique_user: TestUser):
    for route in (api_routes.groups_seeders_foods, api_routes.groups_seeders_units):
        resp = api_client.post(route, json={"locale": "invalid"}, headers=unique_user.token)
        assert resp.status_code == 422


def test_seed_foods(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos

    foods = database.ingredient_foods.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert len(foods) == 0

    resp = api_client.post(api_routes.groups_seeders_foods, json={"locale": LOCALE}, headers=unique_user.token)
    assert resp.status_code == 200

    foods = database.ingredient_foods.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert {food.name for food in foods} == seeded_food_names(LOCALE)


def test_seed_foods_also_seeds_labels(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos

    labels = database.group_multi_purpose_labels.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert len(labels) == 0

    resp = api_client.post(api_routes.groups_seeders_foods, json={"locale": LOCALE}, headers=unique_user.token)
    assert resp.status_code == 200

    labels = database.group_multi_purpose_labels.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert {label.name for label in labels} == seeded_label_names(LOCALE)


def test_seed_foods_links_foods_to_labels(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos

    resp = api_client.post(api_routes.groups_seeders_foods, json={"locale": LOCALE}, headers=unique_user.token)
    assert resp.status_code == 200

    foods = database.ingredient_foods.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert foods
    # every seeded food belongs to one of the seeded labels
    assert all(food.label is not None for food in foods)
    assert {food.label.name for food in foods if food.label} <= seeded_label_names(LOCALE)


def test_seed_units(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos

    units = database.ingredient_units.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert len(units) == 0

    resp = api_client.post(api_routes.groups_seeders_units, json={"locale": LOCALE}, headers=unique_user.token)
    assert resp.status_code == 200

    units = database.ingredient_units.page_all(PaginationQuery(page=1, per_page=-1)).items
    assert {unit.name for unit in units} == seeded_unit_names(LOCALE)

    # Check that the "pint" unit was created and includes standardized data
    pint_found = False
    for unit in units:
        if unit.name != "pint":
            continue

        pint_found = True
        assert unit.standard_quantity == 2
        assert unit.standard_unit == "cup"

    assert pint_found
