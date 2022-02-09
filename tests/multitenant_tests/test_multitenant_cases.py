from typing import Type

import pytest
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from tests.fixtures.fixture_multitenant import MultiTenant
from tests.multitenant_tests.case_abc import ABCMultiTenanatTestCase
from tests.multitenant_tests.case_foods import FoodsTestCase
from tests.multitenant_tests.case_tools import ToolsTestCase
from tests.multitenant_tests.case_units import UnitsTestCase

all_cases = [
    UnitsTestCase,
    FoodsTestCase,
    ToolsTestCase,
]


@pytest.mark.parametrize("test_case", all_cases)
def test_multitenant_cases_get_all(
    api_client: TestClient,
    multitenants: MultiTenant,
    database: AllRepositories,
    test_case: Type[ABCMultiTenanatTestCase],
):
    user1 = multitenants.user_one
    user2 = multitenants.user_two

    test_case = test_case(database, api_client)

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
