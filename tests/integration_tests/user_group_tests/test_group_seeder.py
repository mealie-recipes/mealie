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


def test_seed_foods_second_locale_is_not_skipped(api_client: TestClient, unique_user: TestUser):
    """Seeding a second locale must not be skipped just because the English foods already exist.

    Regression test for #7409: de-duplication keyed off the English seed key rather than the
    localized name, so seeding da-DK after en-US silently created nothing.
    """
    database = unique_user.repos
    other_locale = "da-DK"

    resp = api_client.post(api_routes.groups_seeders_foods, json={"locale": LOCALE}, headers=unique_user.token)
    assert resp.status_code == 200

    resp = api_client.post(api_routes.groups_seeders_foods, json={"locale": other_locale}, headers=unique_user.token)
    assert resp.status_code == 200

    foods = database.ingredient_foods.page_all(PaginationQuery(page=1, per_page=-1)).items
    food_names = {food.name for food in foods}

    # every food unique to the second locale should have been created alongside the English ones
    english_names = seeded_food_names(LOCALE)
    danish_names = seeded_food_names(other_locale)
    assert english_names <= food_names
    assert danish_names - english_names
    assert (danish_names - english_names) <= food_names


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
