from mealie.repos.repository_factory import AllRepositories
from tests.fixtures.fixture_multitenant import MultiTenant


def test_multitenant_recipe_data_storage(
    multitenants: MultiTenant,
    database: AllRepositories,
):
    pass
