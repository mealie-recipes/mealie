import time
from random import randint
from urllib.parse import parse_qsl, urlsplit

import pytest
from fastapi.testclient import TestClient
from humps import camelize

from mealie.repos.repository_factory import AllRepositories
from mealie.repos.repository_units import RepositoryUnit
from mealie.schema.recipe.recipe_ingredient import IngredientUnit, SaveIngredientUnit
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.seeder.seeder_service import SeederService
from tests.utils.fixture_schemas import TestUser


def test_repository_pagination(database: AllRepositories, unique_user: TestUser):
    group = database.groups.get_one(unique_user.group_id)

    seeder = SeederService(database, None, group)
    seeder.seed_foods("en-US")

    foods_repo = database.ingredient_foods.by_group(unique_user.group_id)  # type: ignore

    query = PaginationQuery(
        page=1,
        order_by="id",
        per_page=10,
    )

    seen = []

    for _ in range(10):
        results = foods_repo.page_all(query)

        assert len(results.items) == 10

        for result in results.items:
            assert result.id not in seen

        seen += [result.id for result in results.items]

        query.page += 1

    results = foods_repo.page_all(query)

    for result in results.items:
        assert result.id not in seen


def test_pagination_response_and_metadata(database: AllRepositories, unique_user: TestUser):
    group = database.groups.get_one(unique_user.group_id)

    seeder = SeederService(database, None, group)
    seeder.seed_foods("en-US")

    foods_repo = database.ingredient_foods.by_group(unique_user.group_id)  # type: ignore

    # this should get all results
    query = PaginationQuery(
        page=1,
        per_page=-1,
    )

    all_results = foods_repo.page_all(query)
    assert all_results.total == len(all_results.items)

    # this should get the last page of results
    query = PaginationQuery(
        page=-1,
        per_page=1,
    )

    last_page_of_results = foods_repo.page_all(query)
    assert last_page_of_results.page == last_page_of_results.total_pages
    assert last_page_of_results.items[-1] == all_results.items[-1]


def test_pagination_guides(database: AllRepositories, unique_user: TestUser):
    group = database.groups.get_one(unique_user.group_id)

    seeder = SeederService(database, None, group)
    seeder.seed_foods("en-US")

    foods_repo = database.ingredient_foods.by_group(unique_user.group_id)  # type: ignore
    foods_route = (
        "/foods"  # this doesn't actually have to be accurate, it's just a placeholder to test for query params
    )

    query = PaginationQuery(page=1, per_page=1)

    first_page_of_results = foods_repo.page_all(query)
    first_page_of_results.set_pagination_guides(foods_route, query.dict())
    assert first_page_of_results.next is not None
    assert first_page_of_results.previous is None

    query = PaginationQuery(page=-1, per_page=1)

    last_page_of_results = foods_repo.page_all(query)
    last_page_of_results.set_pagination_guides(foods_route, query.dict())
    assert last_page_of_results.next is None
    assert last_page_of_results.previous is not None

    random_page = randint(2, first_page_of_results.total_pages - 1)
    query = PaginationQuery(page=random_page, per_page=1, filter_string="createdAt>2021-02-22")

    random_page_of_results = foods_repo.page_all(query)
    random_page_of_results.set_pagination_guides(foods_route, query.dict())

    next_params = dict(parse_qsl(urlsplit(random_page_of_results.next).query))
    assert int(next_params["page"]) == random_page + 1

    prev_params = dict(parse_qsl(urlsplit(random_page_of_results.previous).query))
    assert int(prev_params["page"]) == random_page - 1

    source_params = camelize(query.dict())
    for source_param in source_params:
        assert source_param in next_params
        assert source_param in prev_params


@pytest.fixture(scope="function")
def query_units(database: AllRepositories, unique_user: TestUser):
    unit_1 = database.ingredient_units.create(
        SaveIngredientUnit(name="test unit 1", group_id=unique_user.group_id, use_abbreviation=True)
    )

    # wait a moment so we can test datetime filters
    time.sleep(0.25)

    unit_2 = database.ingredient_units.create(
        SaveIngredientUnit(name="test unit 2", group_id=unique_user.group_id, use_abbreviation=False)
    )

    # wait a moment so we can test datetime filters
    time.sleep(0.25)

    unit_3 = database.ingredient_units.create(
        SaveIngredientUnit(name="test unit 3", group_id=unique_user.group_id, use_abbreviation=False)
    )

    unit_ids = [unit.id for unit in [unit_1, unit_2, unit_3]]
    units_repo = database.ingredient_units.by_group(unique_user.group_id)  # type: ignore

    # make sure we can get all of our test units
    query = PaginationQuery(page=1, per_page=-1)
    all_units = units_repo.page_all(query).items
    assert len(all_units) == 3

    for unit in all_units:
        assert unit.id in unit_ids

    yield units_repo, unit_1, unit_2, unit_3

    for unit_id in unit_ids:
        units_repo.delete(unit_id)


def test_pagination_filter_basic(query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]):
    units_repo = query_units[0]
    unit_2 = query_units[2]

    query = PaginationQuery(page=1, per_page=-1, query_filter='name="test unit 2"')
    unit_results = units_repo.page_all(query).items
    assert len(unit_results) == 1
    assert unit_results[0].id == unit_2.id


def test_pagination_filter_datetimes(
    query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]
):
    units_repo = query_units[0]
    unit_1 = query_units[1]
    unit_2 = query_units[2]

    dt = unit_2.created_at.isoformat()
    query = PaginationQuery(page=1, per_page=-1, query_filter=f'createdAt>="{dt}"')
    unit_results = units_repo.page_all(query).items
    assert len(unit_results) == 2
    assert unit_1.id not in [unit.id for unit in unit_results]


def test_pagination_filter_booleans(query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]):
    units_repo = query_units[0]
    unit_1 = query_units[1]

    query = PaginationQuery(page=1, per_page=-1, query_filter="useAbbreviation=true")
    unit_results = units_repo.page_all(query).items
    assert len(unit_results) == 1
    assert unit_results[0].id == unit_1.id


def test_pagination_filter_advanced(query_units: tuple[RepositoryUnit, IngredientUnit, IngredientUnit, IngredientUnit]):
    units_repo = query_units[0]
    unit_3 = query_units[3]

    dt = unit_3.created_at.isoformat()
    qf = f'name="test unit 1" OR (useAbbreviation=f AND (name="test unit 2" OR createdAt > "{dt}"))'
    query = PaginationQuery(page=1, per_page=-1, query_filter=qf)
    unit_results = units_repo.page_all(query).items
    assert len(unit_results) == 2
    assert unit_3.id not in [unit.id for unit in unit_results]


@pytest.mark.parametrize(
    "qf",
    [
        pytest.param('(name="test name" AND useAbbreviation=f))', id="unbalanced parenthesis"),
        pytest.param('createdAt="this is not a valid datetime format"', id="invalid datetime format"),
        pytest.param('badAttribute="test value"', id="invalid attribute"),
    ],
)
def test_malformed_query_filters(api_client: TestClient, unique_user: TestUser, qf: str):
    # verify that improper queries throw 400 errors
    route = "/api/units"

    response = api_client.get(route, params={"queryFilter": qf}, headers=unique_user.token)
    assert response.status_code == 400
