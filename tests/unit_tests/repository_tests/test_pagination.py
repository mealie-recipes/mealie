from random import randint
from urllib.parse import parse_qsl, urlsplit

from humps import camelize

from mealie.repos.repository_factory import AllRepositories
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

    query = PaginationQuery(
        page=1,
        per_page=1,
    )

    first_page_of_results = foods_repo.page_all(query)
    first_page_of_results.set_pagination_guides(foods_route, query.dict())
    assert first_page_of_results.next is not None
    assert first_page_of_results.previous is None

    query = PaginationQuery(
        page=-1,
        per_page=1,
    )

    last_page_of_results = foods_repo.page_all(query)
    last_page_of_results.set_pagination_guides(foods_route, query.dict())
    assert last_page_of_results.next is None
    assert last_page_of_results.previous is not None

    random_page = randint(2, first_page_of_results.total_pages - 1)
    query = PaginationQuery(
        page=random_page,
        per_page=1,
    )

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
