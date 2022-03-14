import pytest
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.fixtures.fixture_multitenant import MultiTenant
from tests.multitenant_tests.case_abc import ABCMultiTenantTestCase
from tests.multitenant_tests.case_categories import CategoryTestCase
from tests.multitenant_tests.case_foods import FoodsTestCase
from tests.multitenant_tests.case_tags import TagsTestCase
from tests.multitenant_tests.case_tools import ToolsTestCase
from tests.multitenant_tests.case_units import UnitsTestCase

all_cases = [
    UnitsTestCase,
    FoodsTestCase,
    ToolsTestCase,
    TagsTestCase,
    CategoryTestCase,
]


@pytest.mark.parametrize("test_case", all_cases)
def test_multitenant_cases_get_all(
    api_client: TestClient,
    multitenants: MultiTenant,
    database: AllRepositories,
    test_case: type[ABCMultiTenantTestCase],
):
    """
    This test will run all the multitenant test cases and validate that they return only the data for their group.
    When requesting all resources.
    """

    user1 = multitenants.user_one
    user2 = multitenants.user_two

    test_case = test_case(database, api_client)

    with test_case:
        expected_ids = test_case.seed_action(user1.group_id)
        expected_results = [
            (user1.token, expected_ids),
            (user2.token, []),
        ]

        for token, item_ids in expected_results:
            response = test_case.get_all(token)
            assert response.status_code == 200

            data = response.json()

            assert len(data) == len(item_ids)

            if len(data) > 0:
                for item in data:
                    assert item["id"] in item_ids


@pytest.mark.parametrize("test_case", all_cases)
def test_multitenant_cases_same_named_resources(
    api_client: TestClient,
    multitenants: MultiTenant,
    database: AllRepositories,
    test_case: type[ABCMultiTenantTestCase],
):
    """
    This test is used to ensure that the same resource can be created with the same values in different tenants.
    i.e. the same category can exist in multiple groups. This is important to validate that the compound unique constraints
    are operating in SQLAlchemy correctly.
    """
    user1 = multitenants.user_one
    user2 = multitenants.user_two

    test_case = test_case(database, api_client)

    with test_case:
        expected_ids, expected_ids2 = test_case.seed_multi(user1.group_id, user2.group_id)
        expected_results = [
            (user1.token, expected_ids),
            (user2.token, expected_ids2),
        ]

        for token, item_ids in expected_results:
            response = test_case.get_all(token)
            assert response.status_code == 200

            data = response.json()

            assert len(data) == len(item_ids)

            if len(data) > 0:
                for item in data:
                    assert item["id"] in item_ids
