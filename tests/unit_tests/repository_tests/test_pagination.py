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
        results = foods_repo.pagination(query)

        assert len(results.data) == 10

        for result in results.data:
            assert result.id not in seen

        seen += [result.id for result in results.data]

        query.page += 1

    results = foods_repo.pagination(query)

    for result in results.data:
        assert result.id not in seen
